"""
AI Engine Views
Handle AI query processing, quality control, and teacher oversight
"""

import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
from django.utils import timezone

from .ai_router import AIRouter
from .quality_assurance import QualityAssuranceEngine
from apps.multi_sector.models import AIInteraction, LearnerProfile, Tenant

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ai_query(request):
    """
    Process AI query with multi-sector routing and quality control
    
    Expected request data:
    {
        "sector": "mathematics|agriculture|tvet",
        "query": "User's educational question",
        "region": "east_africa|west_africa|southern_africa",
        "context": {"additional": "contextual information"}
    }
    """
    try:
        # Extract request data
        sector = request.data.get('sector')
        query = request.data.get('query')
        region = request.data.get('region', 'east_africa')
        context = request.data.get('context', {})
        
        # Validation
        if not sector or not query:
            return Response(
                {'error': 'Both sector and query are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if sector not in ['mathematics', 'agriculture', 'tvet']:
            return Response(
                {'error': 'Invalid sector. Must be mathematics, agriculture, or tvet'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get learner profile and tenant
        try:
            learner_profile = request.user.learner_profile
            tenant = learner_profile.tenant
        except LearnerProfile.DoesNotExist:
            return Response(
                {'error': 'Learner profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Initialize AI router and quality assurance
        ai_router = AIRouter()
        quality_engine = QualityAssuranceEngine()
        
        # Record start time for performance metrics
        start_time = timezone.now()
        
        # Generate AI response
        ai_response = ai_router.route_query(
            sector=sector,
            query=query,
            region=region,
            context=context,
            learner_profile=learner_profile
        )
        
        # Calculate response time
        response_time_ms = int((timezone.now() - start_time).total_seconds() * 1000)
        
        # Quality assurance check
        quality_scores = quality_engine.assess_response(
            response=ai_response,
            sector=sector,
            region=region,
            context=context
        )
        
        # Determine if teacher review is required
        requires_teacher_review = (
            quality_scores.get('cultural_appropriateness', 0) < 
            settings.TEACHER_OVERSIGHT['CULTURAL_SENSITIVITY_THRESHOLD']
            or quality_scores.get('confidence', 0) < 
            settings.TEACHER_OVERSIGHT['AUTO_APPROVE_THRESHOLD']
        )
        
        # Log interaction
        interaction = AIInteraction.objects.create(
            tenant=tenant,
            learner=learner_profile,
            query=query,
            response={
                'content': ai_response.get('content', ''),
                'confidence': ai_response.get('confidence', 0.0),
                'source': ai_response.get('source', 'ai'),
                'requires_review': requires_teacher_review
            },
            sector=sector,
            interaction_type='query',
            quality_scores=quality_scores,
            cultural_appropriateness=quality_scores.get('cultural_appropriateness'),
            response_time_ms=response_time_ms,
            offline_generated=False
        )
        
        # Prepare response
        response_data = {
            'interaction_id': str(interaction.id),
            'content': ai_response.get('content'),
            'confidence': ai_response.get('confidence'),
            'source': ai_response.get('source'),
            'requires_teacher_review': requires_teacher_review,
            'quality_scores': quality_scores,
            'response_time_ms': response_time_ms
        }
        
        # If teacher review required, add review information
        if requires_teacher_review:
            response_data['review_status'] = 'pending_review'
            response_data['message'] = 'Response submitted for teacher review to ensure quality and cultural appropriateness'
        
        logger.info(f"AI query processed: sector={sector}, response_time={response_time_ms}ms, requires_review={requires_teacher_review}")
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error processing AI query: {str(e)}")
        return Response(
            {'error': 'Internal server error processing query'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def interaction_history(request):
    """
    Retrieve interaction history for the current learner
    
    Query parameters:
    - sector: Filter by sector (optional)
    - limit: Number of interactions to return (default: 20)
    """
    try:
        learner_profile = request.user.learner_profile
    except LearnerProfile.DoesNotExist:
        return Response(
            {'error': 'Learner profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Filter parameters
    sector = request.GET.get('sector')
    limit = int(request.GET.get('limit', 20))
    
    # Build query
    interactions = AIInteraction.objects.filter(learner=learner_profile)
    
    if sector:
        interactions = interactions.filter(sector=sector)
    
    interactions = interactions.order_by('-created_at')[:limit]
    
    # Serialize interaction data
    interaction_data = []
    for interaction in interactions:
        interaction_data.append({
            'id': str(interaction.id),
            'query': interaction.query,
            'response': interaction.response,
            'sector': interaction.sector,
            'quality_scores': interaction.quality_scores,
            'teacher_approval': interaction.teacher_approval,
            'created_at': interaction.created_at.isoformat(),
            'response_time_ms': interaction.response_time_ms
        })
    
    return Response({
        'interactions': interaction_data,
        'total_count': len(interaction_data)
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_check(request):
    """
    API health check endpoint
    Returns system status and supported sectors
    """
    try:
        # Test AI router initialization
        ai_router = AIRouter()
        
        # Check sector availability
        available_sectors = []
        for sector in ['mathematics', 'agriculture', 'tvet']:
            if settings.SECTOR_CONFIGS.get(sector, {}).get('enabled', False):
                available_sectors.append(sector)
        
        return Response({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'sectors': available_sectors,
            'features': {
                'offline_sync': True,
                'teacher_oversight': settings.TEACHER_OVERSIGHT['REVIEW_REQUIRED'],
                'multi_tenant': True,
                'cultural_adaptation': True
            },
            'version': '1.0.0-pilot'
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response(
            {'status': 'unhealthy', 'error': str(e)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_feedback(request):
    """
    Submit feedback on AI interaction quality
    
    Expected data:
    {
        "interaction_id": "uuid",
        "helpful": true/false,
        "feedback": "Optional text feedback",
        "cultural_appropriateness": 0.0-1.0
    }
    """
    try:
        interaction_id = request.data.get('interaction_id')
        helpful = request.data.get('helpful')
        feedback_text = request.data.get('feedback', '')
        cultural_score = request.data.get('cultural_appropriateness')
        
        if not interaction_id:
            return Response(
                {'error': 'interaction_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find interaction
        try:
            interaction = AIInteraction.objects.get(
                id=interaction_id,
                learner__user=request.user
            )
        except AIInteraction.DoesNotExist:
            return Response(
                {'error': 'Interaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update interaction with feedback
        feedback_data = {
            'helpful': helpful,
            'feedback': feedback_text,
            'submitted_at': timezone.now().isoformat()
        }
        
        if cultural_score is not None:
            interaction.cultural_appropriateness = cultural_score
            feedback_data['cultural_appropriateness'] = cultural_score
        
        # Store feedback in interaction response
        response_data = interaction.response.copy()
        response_data['user_feedback'] = feedback_data
        interaction.response = response_data
        interaction.save()
        
        logger.info(f"Feedback submitted for interaction {interaction_id}")
        
        return Response({'status': 'feedback_submitted'})
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return Response(
            {'error': 'Internal server error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

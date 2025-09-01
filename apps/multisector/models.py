"""
Multi-sector educational content models
Supports Mathematics, Agriculture, and TVET sectors with cultural adaptation
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class SectorChoices(models.TextChoices):
    MATHEMATICS = 'mathematics', 'Mathematics'
    AGRICULTURE = 'agriculture', 'Agriculture' 
    TVET = 'tvet', 'TVET'

class RegionChoices(models.TextChoices):
    EAST_AFRICA = 'east_africa', 'East Africa'
    WEST_AFRICA = 'west_africa', 'West Africa'
    SOUTHERN_AFRICA = 'southern_africa', 'Southern Africa'
    CENTRAL_AFRICA = 'central_africa', 'Central Africa'

class Tenant(models.Model):
    """Multi-tenant organization model for schools, colleges, extension services"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    sector = models.CharField(max_length=20, choices=SectorChoices.choices)
    region = models.CharField(max_length=20, choices=RegionChoices.choices)
    country = models.CharField(max_length=100)
    
    # Configuration settings for sector-specific behavior
    settings = models.JSONField(default=dict, help_text="Tenant-specific configuration")
    
    # Subscription and billing
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tenants'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.sector}, {self.country})"

class EducationalContent(models.Model):
    """Sector-specific educational content with cultural adaptation"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='content')
    
    # Content classification
    sector = models.CharField(max_length=20, choices=SectorChoices.choices)
    content_type = models.CharField(max_length=100)  # 'lesson', 'exercise', 'hint', etc.
    title = models.CharField(max_length=255)
    
    # Content data (flexible JSON structure)
    content = models.JSONField(help_text="Structured educational content")
    
    # Cultural and regional adaptation
    cultural_context = models.JSONField(
        default=dict, 
        help_text="Cultural adaptation metadata (language, examples, currency, etc.)"
    )
    
    # Quality metrics
    quality_score = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Review and approval status
    review_status = models.CharField(
        max_length=20, 
        choices=[
            ('pending', 'Pending Review'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
            ('needs_revision', 'Needs Revision')
        ],
        default='pending'
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'educational_content'
        indexes = [
            models.Index(fields=['sector', 'content_type']),
            models.Index(fields=['tenant', 'review_status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.sector})"

class LearnerProfile(models.Model):
    """Learner profiles with sector-specific learning patterns"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learner_profile')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='learners')
    
    # Demographics (anonymized for privacy)
    age_group = models.CharField(
        max_length=20,
        choices=[
            ('10-14', '10-14 years'),
            ('15-17', '15-17 years'), 
            ('18-25', '18-25 years'),
            ('26-40', '26-40 years'),
            ('41+', '41+ years')
        ]
    )
    
    # Sector-specific preferences
    primary_sector = models.CharField(max_length=20, choices=SectorChoices.choices)
    learning_preferences = models.JSONField(
        default=dict,
        help_text="Learning style preferences and accessibility needs"
    )
    
    # Performance tracking (anonymized)
    engagement_score = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'learner_profiles'
    
    def __str__(self):
        return f"Learner {self.user.username} ({self.primary_sector})"

class AIInteraction(models.Model):
    """Log of AI interactions with quality and cultural appropriateness tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='interactions')
    learner = models.ForeignKey(LearnerProfile, on_delete=models.CASCADE, related_name='interactions')
    
    # Query and response data
    query = models.TextField(help_text="Student/learner question or request")
    response = models.JSONField(help_text="AI-generated response with metadata")
    
    # Classification
    sector = models.CharField(max_length=20, choices=SectorChoices.choices)
    interaction_type = models.CharField(max_length=50)  # 'question', 'hint_request', etc.
    
    # Quality scores
    quality_scores = models.JSONField(
        default=dict,
        help_text="Detailed quality assessment scores"
    )
    cultural_appropriateness = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]
    )
    
    # Teacher approval
    teacher_approval = models.BooleanField(null=True, blank=True)
    teacher_feedback = models.TextField(blank=True)
    
    # Performance metrics
    response_time_ms = models.IntegerField(null=True, blank=True)
    offline_generated = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_interactions'
        indexes = [
            models.Index(fields=['tenant', 'sector', 'created_at']),
            models.Index(fields=['learner', 'created_at']),
            models.Index(fields=['teacher_approval']),
        ]
    
    def __str__(self):
        return f"Interaction {self.id} ({self.sector})"

class OfflineContent(models.Model):
    """Cached content for offline access, prioritized by sector and region"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='offline_content')
    
    # Content reference
    content = models.ForeignKey(EducationalContent, on_delete=models.CASCADE, related_name='offline_cache')
    
    # Caching metadata
    priority = models.CharField(
        max_length=10,
        choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')],
        default='medium'
    )
    
    # Usage tracking
    access_count = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)
    
    # Sync status
    sync_status = models.CharField(
        max_length=20,
        choices=[
            ('cached', 'Cached'),
            ('pending_sync', 'Pending Sync'),
            ('synced', 'Synced'),
            ('conflict', 'Sync Conflict')
        ],
        default='cached'
    )
    
    cached_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'offline_content'
        unique_together = ['tenant', 'content']
        indexes = [
            models.Index(fields=['priority', 'cached_at']),
            models.Index(fields=['sync_status']),
        ]

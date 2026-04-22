import pytest
from socialmedia import EngagementEngine  

class TestEngagementEngine:
    
    def test_init(self):
        """Test basic initialization."""
        engine = EngagementEngine("test_user")
        assert engine.user_handle == "test_user"
        assert engine.score == 0.0
        assert engine.verified == False
        
        engine_verified = EngagementEngine("verified_user", verified=True)
        assert engine_verified.verified == True

    def test_process_interaction_valid(self):
        """Test valid interaction processing."""
        engine = EngagementEngine("user1")
        assert engine.process_interaction("like", 1) == True
        assert engine.score == 1.0
        
        engine.process_interaction("comment", 2)
        assert engine.score == 11.0
        
        engine.process_interaction("share", 1)
        assert engine.score == 21.0

    def test_process_interaction_verified_multiplier(self):
        """Test verified user score multiplier."""
        engine = EngagementEngine("verified_user", verified=True)
        engine.process_interaction("like", 1)
        assert engine.score == 1.5
        
        engine.process_interaction("comment", 1)
        assert engine.score == 6.5

    def test_process_interaction_negative_count(self):
        """Test negative count raises ValueError."""
        engine = EngagementEngine("user1")
        with pytest.raises(ValueError, match="Negative count"):
            engine.process_interaction("like", -1)

    def test_process_interaction_invalid_type(self):
        """Test invalid interaction type returns False."""
        engine = EngagementEngine("user1")
        result = engine.process_interaction("invalid")
        assert result == False
        assert engine.score == 0.0

    def test_get_tier_progression(self):
        """Test tier progression based on score."""
        engine = EngagementEngine("user1")
        
        engine.score = 50
        assert engine.get_tier() == "Newbie"
        
        engine.score = 500
        assert engine.get_tier() == "Influencer"
        
        engine.score = 1500
        assert engine.get_tier() == "Icon"

    def test_get_tier_boundary_conditions(self):
        """Test exact boundary conditions for tiers."""
        engine = EngagementEngine("user1")
        
        engine.score = 99.9
        assert engine.get_tier() == "Newbie"
        
        engine.score = 100.0
        assert engine.get_tier() == "Influencer"
        
        engine.score = 1000.0
        assert engine.get_tier() == "Influencer"
        
        engine.score = 1000.1
        assert engine.get_tier() == "Icon"

    def test_apply_penalty_small_reports(self):
        """Test penalty with small report count."""
        engine = EngagementEngine("user1", verified=True)
        engine.score = 1000
        engine.apply_penalty(5)
        
        assert engine.verified == True
        assert engine.score == 900.0

    def test_apply_penalty_large_reports(self):
        """Test penalty that revokes verification."""
        engine = EngagementEngine("user1", verified=True)
        engine.score = 1000
        engine.apply_penalty(15)
        
        assert engine.verified == False
        assert engine.score == 700.0

    def test_apply_penalty_zero_score(self):
        """Test penalty on zero score doesn't go negative."""
        engine = EngagementEngine("user1")
        engine.score = 0
        engine.apply_penalty(10)
        assert engine.score == 0

    def test_integration_full_cycle(self):
        """Test full engagement cycle."""
        engine = EngagementEngine("full_user", verified=True)
        
        engine.process_interaction("share", 10)
        engine.process_interaction("comment", 20)
        assert engine.score == 175.0
        assert engine.get_tier() == "Newbie"
        
        engine.apply_penalty(3)
        assert engine.score == 142.5
        assert engine.verified == True
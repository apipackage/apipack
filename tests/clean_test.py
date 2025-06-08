"""Clean test file to verify pytest is working."""

def test_addition():
    """Test basic addition."""
    assert 1 + 1 == 2

class TestSimple:
    """Test class with simple assertions."""
    
    def test_subtraction(self):
        """Test basic subtraction."""
        assert 3 - 1 == 2

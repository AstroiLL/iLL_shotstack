#!/usr/bin/env python3
"""Integration tests for validation workflow."""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

from fast_clip.check.validation import (
    JsonValidator,
    FileChecker,
    FieldValidator,
    ValidationLevel
)


class TestValidationWorkflow:
    """Integration tests for complete validation workflow."""
    
    def test_full_validation_workflow(self):
        """Test complete validation workflow with all validators."""
        # Create test data with various issues
        test_data = {
            "template": {
                "timeline": {
                    "tracks": [
                        {
                            "clips": [
                                {
                                    "asset": {
                                        "type": "video",
                                        "src": "{{test_video.mp4}}"
                                    },
                                    "start": 0.0,
                                    "length": 5.0,
                                    "transition": {
                                        "in": "invalidTransition",  # Invalid transition
                                        "out": "fade"
                                    },
                                    "effect": "zoomIn",  # Valid effect
                                    "filter": "boost"  # Valid filter
                                }
                            ]
                        }
                    ]
                }
            },
            "output": {
                "format": "mp4",
                "aspectRatio": "16:9"  # Valid aspect ratio
            },
            "merge": [
                {"find": "test_video.mp4", "replace": ""}
            ]
        }
        
        # Initialize all validators
        json_validator = JsonValidator(strict_mode=False)
        file_checker = FileChecker(strict_mode=False, script_path=Path("/tmp"))
        field_validator = FieldValidator(strict_mode=False)
        
        # Run validation
        json_report = json_validator.validate(test_data)
        file_report = file_checker.validate(test_data)
        field_report = field_validator.validate(test_data)
        
        # JSON validation should pass (structure is valid)
        assert json_report.is_valid
        
        # File validation should have warnings (file doesn't exist)
        assert file_report.total_warnings > 0
        
        # Field validation should have warnings (invalid transition)
        assert field_report.total_warnings > 0
    
    def test_convert_script_integration(self):
        """Test integration with convert_script.py."""
        # Create a temporary markdown file
        md_content = """# Test Script

| Text | Description | Clip | Sound effect |
|-------|-------------|--------|--------------|
| Test | Test video | test.mp4 | |

"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(md_content)
            md_path = Path(f.name)
        
        try:
            # Import convert_script to test integration
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from convert_script import convert_file
            
            # Test conversion with validation
            result = convert_file(md_path, validate_output=True, strict_mode=False)
            
            # Should return None due to validation failure (missing file)
            assert result is None
            
        finally:
            # Clean up
            if md_path.exists():
                md_path.unlink()
    
    def test_check_script_integration(self):
        """Test integration with check.py."""
        # Create test JSON file
        test_data = {
            "template": {
                "timeline": {
                    "tracks": [
                        {
                            "clips": [
                                {
                                    "asset": {
                                        "type": "video",
                                        "src": "{{test.mp4}}"
                                    },
                                    "start": 0.0,
                                    "length": 5.0
                                }
                            ]
                        }
                    ]
                }
            },
            "output": {"format": "mp4"},
            "merge": [
                {"find": "test.mp4", "replace": ""}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, indent=2)
            json_path = Path(f.name)
        
        try:
            # Import check.py to test integration
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from check import check_script
            
            # Test checking with new validation system
            is_valid, results = check_script(json_path, verbose=False, quiet=True)
            
            # Should have warnings (file doesn't exist)
            assert not is_valid  # File validation should fail
            assert len(results) > 0
            
        finally:
            # Clean up
            if json_path.exists():
                json_path.unlink()
    
    def test_assemble_script_integration(self):
        """Test integration with assemble.py."""
        # Create test script file
        test_data = {
            "template": {
                "timeline": {
                    "tracks": [
                        {
                            "clips": [
                                {
                                    "asset": {
                                        "type": "video",
                                        "src": "{{test.mp4}}"
                                    },
                                    "start": 0.0,
                                    "length": 5.0
                                }
                            ]
                        }
                    ]
                }
            },
            "output": {"format": "mp4"},
            "merge": [
                {"find": "test.mp4", "replace": "https://example.com/test.mp4"}
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f, indent=2)
            script_path = Path(f.name)
        
        try:
            # Test file validation (without full assembler)
            json_validator = JsonValidator(strict_mode=False)
            file_checker = FileChecker(strict_mode=False, script_path=script_path)
            field_validator = FieldValidator(strict_mode=False)
            
            # Run validation
            json_report = json_validator.validate(test_data)
            file_report = file_checker.validate(test_data)
            field_report = field_validator.validate(test_data)
            
            # Should pass all validation (URL is not a local file)
            assert json_report.is_valid
            assert file_report.is_valid
            assert field_report.is_valid
            
        finally:
            # Clean up
            if script_path.exists():
                script_path.unlink()


class TestValidationEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_template(self):
        """Test validation of empty template."""
        validator = JsonValidator()
        
        data = {
            "template": {},
            "output": {"format": "mp4"},
            "merge": []
        }
        
        report = validator.validate(data)
        assert not report.is_valid
        assert any("timeline" in r.message.lower() for r in report.results if r.level == ValidationLevel.ERROR)
    
    def test_malformed_placeholder_syntax(self):
        """Test various malformed placeholder syntaxes."""
        validator = JsonValidator()
        
        test_cases = [
            "{{field",  # Missing closing brace
            "field}}",  # Missing opening brace
            "{field}",  # Single braces
            "{{}}",  # Empty placeholder
        ]
        
        for invalid_placeholder in test_cases:
            data = {
                "template": {
                    "timeline": {
                        "tracks": [
                            {
                                "clips": [
                                    {
                                        "asset": {
                                            "type": "video",
                                            "src": invalid_placeholder
                                        },
                                        "start": 0.0,
                                        "length": 5.0
                                    }
                                ]
                            }
                        ]
                    }
                },
                "output": {"format": "mp4"},
                "merge": []
            }
            
            report = validator.validate(data)
            # Should have warnings for placeholder syntax issues
            assert report.total_warnings > 0
    
    def test_large_complex_script(self):
        """Test validation of large, complex script."""
        validator = JsonValidator()
        
        # Create a complex script with many tracks and clips
        data = {
            "template": {
                "timeline": {
                    "tracks": [
                        {
                            "clips": [
                                {
                                    "asset": {"type": "video", "src": f"video_{i}.mp4"}},
                                    "start": float(i * 5.0),
                                    "length": 5.0,
                                    "transition": {
                                        "in": "fade" if i % 2 == 0 else "slideLeft",
                                        "out": "fade" if i % 3 == 0 else "slideRight"
                                    }
                                } for i in range(20)  # 20 clips
                            ]
                        } for _ in range(3)  # 3 tracks
                    ]
                }
            },
            "output": {"format": "mp4"},
            "merge": [
                {"find": f"video_{i}.mp4", "replace": f"https://example.com/video_{i}.mp4"}
                for i in range(20)
            ]
        }
        
        report = validator.validate(data)
        # Should handle large scripts without issues
        assert report.is_valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
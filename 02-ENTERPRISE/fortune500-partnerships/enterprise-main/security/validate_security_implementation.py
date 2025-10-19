#!/usr/bin/env python3
"""
Security Implementation Validation Script
========================================

This script validates that all security hardening components are properly
implemented and functioning correctly.

Usage:
    python validate_security_implementation.py

The script will:
1. Test production cryptography functions
2. Validate secure configuration management
3. Test JWT security components
4. Verify input validation middleware
5. Check CORS security configuration
6. Run basic security tests
7. Generate a comprehensive validation report
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SecurityValidationResult:
    """Security validation result tracking"""

    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.errors = []
        self.warnings = []
        self.start_time = datetime.utcnow()
        self.results = {}

    def add_test_result(self, component: str, test_name: str, passed: bool, message: str = ""):
        """Add a test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            status = "PASS"
        else:
            self.tests_failed += 1
            status = "FAIL"
            self.errors.append(f"{component}.{test_name}: {message}")

        if component not in self.results:
            self.results[component] = []

        self.results[component].append({
            "test": test_name,
            "status": status,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })

        logger.info(f"{status}: {component}.{test_name} - {message}")

    def add_warning(self, message: str):
        """Add a warning message"""
        self.warnings.append(message)
        logger.warning(message)

    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        end_time = datetime.utcnow()
        duration = (end_time - self.start_time).total_seconds()

        return {
            "validation_summary": {
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "tests_run": self.tests_run,
                "tests_passed": self.tests_passed,
                "tests_failed": self.tests_failed,
                "success_rate": (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0,
                "overall_status": "PASS" if self.tests_failed == 0 else "FAIL"
            },
            "component_results": self.results,
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": self._generate_recommendations()
        }

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on results"""
        recommendations = []

        if self.tests_failed > 0:
            recommendations.append("Address failed security tests before deployment")

        if len(self.warnings) > 0:
            recommendations.append("Review security warnings and implement improvements")

        if self.tests_passed == self.tests_run:
            recommendations.append("Security implementation validated successfully - ready for deployment")
        else:
            recommendations.append("Security implementation needs attention before production use")

        return recommendations

async def validate_production_cryptography():
    """Validate production cryptography implementation"""
    result = SecurityValidationResult()

    try:
        from aia.crypto.production_cryptography import ProductionCryptography, SecurityLevel

        crypto = ProductionCryptography(SecurityLevel.HIGH)
        result.add_test_result("crypto", "import", True, "Production cryptography imported successfully")

        # Test DID generation
        try:
            did_doc = crypto.generate_did("test-validation")
            result.add_test_result("crypto", "did_generation", True, f"DID generated: {did_doc.did[:50]}...")
        except Exception as e:
            result.add_test_result("crypto", "did_generation", False, str(e))

        # Test encryption/decryption
        try:
            test_data = "This is sensitive test data for validation"
            encrypted = crypto.encrypt_data(test_data)
            decrypted = crypto.decrypt_data(encrypted)

            success = decrypted.decode() == test_data
            result.add_test_result("crypto", "encryption", success, "Encryption/decryption cycle completed")
        except Exception as e:
            result.add_test_result("crypto", "encryption", False, str(e))

        # Test key derivation
        try:
            derived_key = crypto.derive_key("test-password", algorithm=crypto.CryptoAlgorithm.ARGON2ID)
            result.add_test_result("crypto", "key_derivation", len(derived_key) == 32, f"Key derived: {len(derived_key)} bytes")
        except Exception as e:
            result.add_test_result("crypto", "key_derivation", False, str(e))

        # Test secure token generation
        try:
            token = crypto.generate_secure_token(32)
            result.add_test_result("crypto", "token_generation", len(token) > 30, f"Token generated: {len(token)} chars")
        except Exception as e:
            result.add_test_result("crypto", "token_generation", False, str(e))

    except ImportError as e:
        result.add_test_result("crypto", "import", False, f"Import failed: {e}")
        result.add_warning("Production cryptography not available - using fallback implementations")

    return result

async def validate_secure_configuration():
    """Validate secure configuration management"""
    result = SecurityValidationResult()

    try:
        from aia.config.secure_config import SecureConfigManager, SecretType

        config_manager = SecureConfigManager(environment="testing")
        result.add_test_result("config", "import", True, "Secure config imported successfully")

        # Test secret generation
        try:
            test_secret = config_manager._generate_secret_value(SecretType.JWT_SECRET)
            result.add_test_result("config", "secret_generation", len(test_secret) >= 64, f"Secret generated: {len(test_secret)} chars")
        except Exception as e:
            result.add_test_result("config", "secret_generation", False, str(e))

        # Test secret validation
        try:
            valid = config_manager._validate_secret_strength("weak", SecretType.JWT_SECRET)
            result.add_test_result("config", "secret_validation", not valid, "Weak secret properly rejected")
        except Exception as e:
            result.add_test_result("config", "secret_validation", False, str(e))

        # Test JWT config generation
        try:
            jwt_config = config_manager.get_jwt_config()
            has_secret = "secret" in jwt_config and len(jwt_config["secret"]) > 10
            result.add_test_result("config", "jwt_config", has_secret, "JWT config generated with secret")
        except Exception as e:
            result.add_test_result("config", "jwt_config", False, str(e))

    except ImportError as e:
        result.add_test_result("config", "import", False, f"Import failed: {e}")
        result.add_warning("Secure configuration not available - using environment variables")

    return result

async def validate_jwt_security():
    """Validate enhanced JWT security"""
    result = SecurityValidationResult()

    try:
        from aia.auth.enhanced_jwt_security import EnhancedJWTSecurity, TokenType

        jwt_security = EnhancedJWTSecurity()
        await jwt_security.initialize()
        result.add_test_result("jwt", "import", True, "JWT security imported successfully")

        # Test token generation
        try:
            token_pair = jwt_security.generate_token_pair(
                user_id="test-user",
                scopes=["read", "write"],
                ip_address="192.168.1.1",
                user_agent="Test-Agent"
            )

            has_tokens = token_pair.access_token and token_pair.refresh_token
            result.add_test_result("jwt", "token_generation", has_tokens, "Token pair generated successfully")
        except Exception as e:
            result.add_test_result("jwt", "token_generation", False, str(e))

        # Test token validation
        try:
            validation = await jwt_security.validate_token(
                token_pair.access_token,
                expected_type=TokenType.ACCESS,
                ip_address="192.168.1.1",
                user_agent="Test-Agent"
            )

            result.add_test_result("jwt", "token_validation", validation["valid"], "Token validation successful")
        except Exception as e:
            result.add_test_result("jwt", "token_validation", False, str(e))

        # Test token refresh
        try:
            new_pair = await jwt_security.refresh_token_pair(
                token_pair.refresh_token,
                ip_address="192.168.1.1",
                user_agent="Test-Agent"
            )

            refresh_success = new_pair is not None
            result.add_test_result("jwt", "token_refresh", refresh_success, "Token refresh successful")
        except Exception as e:
            result.add_test_result("jwt", "token_refresh", False, str(e))

    except ImportError as e:
        result.add_test_result("jwt", "import", False, f"Import failed: {e}")
        result.add_warning("Enhanced JWT security not available - using basic JWT")

    return result

async def validate_input_validation():
    """Validate input validation middleware"""
    result = SecurityValidationResult()

    try:
        from aia.api.validation_middleware import InputValidationMiddleware, AttackType

        middleware = InputValidationMiddleware()
        await middleware.initialize()
        result.add_test_result("validation", "import", True, "Input validation imported successfully")

        # Test SQL injection detection
        try:
            sql_detected = middleware._detect_sql_injection("'; DROP TABLE users; --")
            result.add_test_result("validation", "sql_injection", sql_detected, "SQL injection detected correctly")
        except Exception as e:
            result.add_test_result("validation", "sql_injection", False, str(e))

        # Test XSS detection
        try:
            xss_detected = middleware._detect_xss("<script>alert('xss')</script>")
            result.add_test_result("validation", "xss_detection", xss_detected, "XSS attack detected correctly")
        except Exception as e:
            result.add_test_result("validation", "xss_detection", False, str(e))

        # Test command injection detection
        try:
            cmd_detected = middleware._detect_command_injection("; rm -rf /")
            result.add_test_result("validation", "command_injection", cmd_detected, "Command injection detected correctly")
        except Exception as e:
            result.add_test_result("validation", "command_injection", False, str(e))

        # Test path traversal detection
        try:
            path_detected = middleware._detect_path_traversal("../../../etc/passwd")
            result.add_test_result("validation", "path_traversal", path_detected, "Path traversal detected correctly")
        except Exception as e:
            result.add_test_result("validation", "path_traversal", False, str(e))

    except ImportError as e:
        result.add_test_result("validation", "import", False, f"Import failed: {e}")
        result.add_warning("Input validation middleware not available - potential security risk")

    return result

async def validate_cors_security():
    """Validate CORS security configuration"""
    result = SecurityValidationResult()

    try:
        from aia.api.secure_cors import SecureCORSManager, EnvironmentType

        cors_manager = SecureCORSManager(environment=EnvironmentType.PRODUCTION)
        await cors_manager.initialize()
        result.add_test_result("cors", "import", True, "CORS security imported successfully")

        # Test CORS configuration
        try:
            cors_config = cors_manager.get_cors_config()
            has_config = "allow_origins" in cors_config
            result.add_test_result("cors", "configuration", has_config, "CORS configuration generated")
        except Exception as e:
            result.add_test_result("cors", "configuration", False, str(e))

        # Test suspicious pattern detection
        try:
            suspicious = await cors_manager._contains_suspicious_patterns("https://192.168.1.1")
            result.add_test_result("cors", "pattern_detection", suspicious, "Suspicious patterns detected correctly")
        except Exception as e:
            result.add_test_result("cors", "pattern_detection", False, str(e))

    except ImportError as e:
        result.add_test_result("cors", "import", False, f"Import failed: {e}")
        result.add_warning("Secure CORS not available - using permissive CORS configuration")

    return result

async def validate_security_testing():
    """Validate security testing framework"""
    result = SecurityValidationResult()

    try:
        from aia.testing.security_testing_framework import SecurityTestingFramework, VulnerabilityType

        framework = SecurityTestingFramework(base_url="http://localhost:8000")
        result.add_test_result("testing", "import", True, "Security testing framework imported successfully")

        # Test payload loading
        try:
            payloads = framework._load_vulnerability_payloads()
            has_payloads = "sql_injection" in payloads and len(payloads["sql_injection"]) > 0
            result.add_test_result("testing", "payloads", has_payloads, f"Loaded {len(payloads)} payload categories")
        except Exception as e:
            result.add_test_result("testing", "payloads", False, str(e))

        # Test test case loading
        try:
            test_cases = framework._load_test_cases()
            has_cases = len(test_cases) > 0
            result.add_test_result("testing", "test_cases", has_cases, f"Loaded {len(test_cases)} test cases")
        except Exception as e:
            result.add_test_result("testing", "test_cases", False, str(e))

    except ImportError as e:
        result.add_test_result("testing", "import", False, f"Import failed: {e}")
        result.add_warning("Security testing framework not available")

    return result

async def validate_main_integration():
    """Validate main application integration"""
    result = SecurityValidationResult()

    try:
        # Check if main.py has security integration
        main_path = Path("aia/main.py")
        if main_path.exists():
            with open(main_path, 'r') as f:
                main_content = f.read()

            # Check for security imports
            has_security_imports = "secure_config" in main_content and "enhanced_jwt" in main_content
            result.add_test_result("integration", "security_imports", has_security_imports, "Security components imported in main.py")

            # Check for security initialization
            has_security_init = "initialize_security" in main_content
            result.add_test_result("integration", "security_init", has_security_init, "Security initialization present")

            # Check for middleware integration
            has_middleware = "validation_middleware" in main_content
            result.add_test_result("integration", "middleware", has_middleware, "Validation middleware integrated")

        else:
            result.add_test_result("integration", "main_file", False, "main.py not found")

    except Exception as e:
        result.add_test_result("integration", "check", False, str(e))

    return result

async def run_comprehensive_validation():
    """Run comprehensive security validation"""
    logger.info("🔐 Starting comprehensive security validation...")

    # Run all validation tests
    validation_tasks = [
        validate_production_cryptography(),
        validate_secure_configuration(),
        validate_jwt_security(),
        validate_input_validation(),
        validate_cors_security(),
        validate_security_testing(),
        validate_main_integration()
    ]

    # Execute all validations concurrently
    validation_results = await asyncio.gather(*validation_tasks, return_exceptions=True)

    # Combine results
    combined_result = SecurityValidationResult()
    combined_result.start_time = min(
        [r.start_time for r in validation_results if isinstance(r, SecurityValidationResult)]
    )

    for result in validation_results:
        if isinstance(result, SecurityValidationResult):
            combined_result.tests_run += result.tests_run
            combined_result.tests_passed += result.tests_passed
            combined_result.tests_failed += result.tests_failed
            combined_result.errors.extend(result.errors)
            combined_result.warnings.extend(result.warnings)
            combined_result.results.update(result.results)
        else:
            # Handle exceptions
            combined_result.errors.append(f"Validation error: {str(result)}")

    return combined_result

def print_validation_summary(result: SecurityValidationResult):
    """Print validation summary to console"""
    report = result.generate_report()

    print("\n" + "="*80)
    print("🛡️  AIA SECURITY VALIDATION REPORT")
    print("="*80)

    summary = report["validation_summary"]
    print(f"Duration: {summary['duration_seconds']:.2f} seconds")
    print(f"Tests Run: {summary['tests_run']}")
    print(f"Tests Passed: {summary['tests_passed']}")
    print(f"Tests Failed: {summary['tests_failed']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Overall Status: {summary['overall_status']}")

    if summary['overall_status'] == 'PASS':
        print("\n✅ SECURITY VALIDATION PASSED")
        print("   All security components are properly implemented and functional.")
    else:
        print("\n❌ SECURITY VALIDATION FAILED")
        print("   Some security components need attention before production deployment.")

    # Component summary
    print(f"\n📊 COMPONENT SUMMARY:")
    for component, tests in report["component_results"].items():
        passed = sum(1 for t in tests if t["status"] == "PASS")
        total = len(tests)
        print(f"   {component}: {passed}/{total} tests passed")

    # Errors
    if report["errors"]:
        print(f"\n🚨 ERRORS ({len(report['errors'])}):")
        for error in report["errors"]:
            print(f"   • {error}")

    # Warnings
    if report["warnings"]:
        print(f"\n⚠️  WARNINGS ({len(report['warnings'])}):")
        for warning in report["warnings"]:
            print(f"   • {warning}")

    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    for rec in report["recommendations"]:
        print(f"   • {rec}")

    print("="*80)

async def main():
    """Main validation function"""
    try:
        # Run comprehensive validation
        result = await run_comprehensive_validation()

        # Print summary
        print_validation_summary(result)

        # Save detailed report
        report = result.generate_report()
        report_file = f"security_validation_report_{int(time.time())}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n📄 Detailed report saved to: {report_file}")

        # Exit with appropriate code
        if result.tests_failed > 0:
            print("\n❌ Validation failed - security components need attention")
            sys.exit(1)
        else:
            print("\n✅ Validation successful - security implementation ready")
            sys.exit(0)

    except Exception as e:
        logger.error(f"Validation failed with error: {e}")
        print(f"\n💥 CRITICAL ERROR: {e}")
        sys.exit(2)

if __name__ == "__main__":
    asyncio.run(main())
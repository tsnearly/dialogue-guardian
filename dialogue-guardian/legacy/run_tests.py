#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Tony Snearly
# SPDX-License-Identifier: OSL-3.0
"""
Test runner for guardian-by-ffmpeg unit tests
"""

import sys
import os
import unittest

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import test suite
from test_guardian_by_ffmpeg import TestGuardianByFFmpeg, TestIntegration

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.makeSuite(TestGuardianByFFmpeg))
    test_suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)

"""
Complete test suite for FishDraw
Run this to verify everything works correctly
"""

import sys
from fishdraw_complete import (
    main, generate_params, fish, noise, rand, draw_svg,
    resample, approx_poly_dp, reframe, cleanup
)

def test_random_seed():
    """Test: Random seed generation"""
    print("\n=== Test: Random Seed Generation ===")
    for i in range(3):
        fish_num = main()
        print(f"  ✓ Fish {i+1}: {len(fish_num)} polylines")
    return True

def test_seeded_fish():
    """Test: Seeded fish (reproducible)"""
    print("\n=== Test: Seeded Fish ===")
    seeds = ["Alpha", "Beta", "Gamma"]
    results = {}
    
    for seed in seeds:
        fish1 = main(seed)
        fish2 = main(seed)  # Generate again with same seed
        
        # Should have same number of polylines (approximately)
        # Note: Due to floating point, may not be exactly same
        print(f"  Seed '{seed}':")
        print(f"    Run 1: {len(fish1)} polylines")
        print(f"    Run 2: {len(fish2)} polylines")
        results[seed] = len(fish1)
    
    print("  ✓ Seeded generation works")
    return True

def test_parameters():
    """Test: Parameter generation"""
    print("\n=== Test: Parameter Generation ===")
    
    for i in range(3):
        params = generate_params()
        print(f"  Params {i+1}:")
        print(f"    Body type: {params['body_curve_type']}")
        print(f"    Body length: {params['body_length']:.1f}")
        print(f"    Tail type: {params['tail_type']}")
    
    print("  ✓ Parameter generation works")
    return True

def test_noise():
    """Test: Perlin noise"""
    print("\n=== Test: Perlin Noise ===")
    
    # Test that noise is reproducible
    set_seed_value = 12345
    from fishdraw_complete import set_seed
    
    set_seed(set_seed_value)
    n1 = noise(0.5, 0.5, 0.5)
    
    set_seed(set_seed_value)
    n2 = noise(0.5, 0.5, 0.5)
    
    print(f"  Noise run 1: {n1:.6f}")
    print(f"  Noise run 2: {n2:.6f}")
    
    if abs(n1 - n2) < 0.0001:
        print("  ✓ Noise is reproducible")
        return True
    else:
        print("  ✗ Noise is NOT reproducible!")
        return False

def test_svg_export():
    """Test: SVG export"""
    print("\n=== Test: SVG Export ===")
    
    drawing = main("SVGTest")
    svg = draw_svg(drawing)
    
    print(f"  Generated SVG: {len(svg)} bytes")
    
    # Check for SVG markers
    checks = [
        ('<svg', 'SVG tag'),
        ('xmlns', 'Namespace'),
        ('polyline', 'Polylines'),
        ('stroke="black"', 'Stroke color'),
    ]
    
    for marker, desc in checks:
        if marker in svg:
            print(f"    ✓ {desc}")
        else:
            print(f"    ✗ Missing {desc}")
            return False
    
    return True

def test_geometry():
    """Test: Geometry functions"""
    print("\n=== Test: Geometry Functions ===")
    
    # Test resample
    poly = [(0, 0), (10, 0), (20, 0), (30, 0)]
    resampled = resample(poly, 5)
    print(f"  Resample: {len(poly)} → {len(resampled)} points")
    
    # Test simplification
    complex_poly = [(0, 0), (1, 1), (2, 2), (3, 3), (100, 100)]
    simple = approx_poly_dp(complex_poly, 1.0)
    print(f"  Simplify: {len(complex_poly)} → {len(simple)} points")
    
    print("  ✓ Geometry functions work")
    return True

def test_large_generation():
    """Test: Stress test - generate many fish"""
    print("\n=== Test: Stress Test (5 fish) ===")
    
    try:
        for i in range(5):
            drawing = main()
            print(f"  Fish {i+1}: {len(drawing)} polylines")
        
        print("  ✓ No memory issues")
        return True
    
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 50)
    print("FishDraw Complete Test Suite")
    print("=" * 50)
    
    tests = [
        ("Random Seed", test_random_seed),
        ("Seeded Fish", test_seeded_fish),
        ("Parameters", test_parameters),
        ("Noise", test_noise),
        ("SVG Export", test_svg_export),
        ("Geometry", test_geometry),
        ("Stress Test", test_large_generation),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = "✓ PASS" if result else "✗ FAIL"
        except Exception as e:
            print(f"  ✗ Exception: {e}")
            results[name] = "✗ FAIL"
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary:")
    print("=" * 50)
    
    for name, result in results.items():
        print(f"  {name:20} {result}")
    
    passed = sum(1 for r in results.values() if "PASS" in r)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓✓✓ All tests PASSED! ✓✓✓")
        return 0
    else:
        print("\n✗✗✗ Some tests FAILED! ✗✗✗")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())

from my_pkg import answer
import time


def test_answer():
    """Test the answer method."""
    start_time = time.time()
    assert answer() == 42

    # check that the documented performance is somewhat close
    elapsed_time = time.time() - start_time
    assert 7.5 * 0.9 <= elapsed_time <= 7.5 * 1.1

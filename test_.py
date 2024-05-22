import os
import app

def test_model_file_created():
    app.main()  # Assuming the main function encapsulates the training logic
    assert os.path.exists('models/model.pkl')

def test_model_score():
    score = app.main()  # Assuming the main function returns the score
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
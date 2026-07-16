import os
import pandas as pd
import numpy as np
import joblib
import pytest
import app


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def sample_raw_data():
    """Return a small raw DataFrame that mimics credit_card_records.csv."""
    return pd.DataFrame({
        "Date": ["2023-01-15", "2023-03-22", "2023-07-04", "2023-11-30", "2023-06-01"],
        "Amount": [120.50, 999.99, 5.00, 450.75, 200.00],
        "Location": ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"],
        "Store": ["Store A", "Store B", "Store C", "Store A", "Store B"],
        "Fraudulent": [True, False, False, True, False],
    })


@pytest.fixture
def preprocessed_data(sample_raw_data):
    """Return pre-processed version of sample_raw_data."""
    return app.preprocess_data(sample_raw_data.copy())


# ---------------------------------------------------------------------------
# Tests for load_data
# ---------------------------------------------------------------------------

def test_load_data_returns_dataframe(tmp_path, sample_raw_data):
    csv_file = tmp_path / "test_data.csv"
    sample_raw_data.to_csv(csv_file, index=False)

    result = app.load_data(str(csv_file))

    assert isinstance(result, pd.DataFrame)


def test_load_data_has_expected_columns(tmp_path, sample_raw_data):
    csv_file = tmp_path / "test_data.csv"
    sample_raw_data.to_csv(csv_file, index=False)

    result = app.load_data(str(csv_file))

    assert set(result.columns) == {"Date", "Amount", "Location", "Store", "Fraudulent"}


def test_load_data_row_count(tmp_path, sample_raw_data):
    csv_file = tmp_path / "test_data.csv"
    sample_raw_data.to_csv(csv_file, index=False)

    result = app.load_data(str(csv_file))

    assert len(result) == len(sample_raw_data)


# ---------------------------------------------------------------------------
# Tests for preprocess_data
# ---------------------------------------------------------------------------

def test_preprocess_data_removes_date_column(sample_raw_data):
    result = app.preprocess_data(sample_raw_data.copy())
    assert "Date" not in result.columns


def test_preprocess_data_adds_year_month_day(sample_raw_data):
    result = app.preprocess_data(sample_raw_data.copy())
    assert "Year" in result.columns
    assert "Month" in result.columns
    assert "Day" in result.columns


def test_preprocess_data_encodes_location_as_int(sample_raw_data):
    result = app.preprocess_data(sample_raw_data.copy())
    assert pd.api.types.is_integer_dtype(result["Location"])


def test_preprocess_data_encodes_store_as_int(sample_raw_data):
    result = app.preprocess_data(sample_raw_data.copy())
    assert pd.api.types.is_integer_dtype(result["Store"])


def test_preprocess_data_preserves_row_count(sample_raw_data):
    result = app.preprocess_data(sample_raw_data.copy())
    assert len(result) == len(sample_raw_data)


# ---------------------------------------------------------------------------
# Tests for split_data
# ---------------------------------------------------------------------------

def test_split_data_returns_four_parts(preprocessed_data):
    splits = app.split_data(preprocessed_data, "Fraudulent")
    assert len(splits) == 4


def test_split_data_sizes(preprocessed_data):
    X_train, X_test, y_train, y_test = app.split_data(preprocessed_data, "Fraudulent", test_size=0.2)
    total = len(preprocessed_data)
    assert len(X_train) + len(X_test) == total
    assert len(y_train) + len(y_test) == total


def test_split_data_target_not_in_features(preprocessed_data):
    X_train, X_test, y_train, y_test = app.split_data(preprocessed_data, "Fraudulent")
    assert "Fraudulent" not in X_train.columns
    assert "Fraudulent" not in X_test.columns


def test_split_data_reproducible_with_same_seed(preprocessed_data):
    X_train_1, X_test_1, _, _ = app.split_data(preprocessed_data, "Fraudulent", random_state=0)
    X_train_2, X_test_2, _, _ = app.split_data(preprocessed_data, "Fraudulent", random_state=0)
    pd.testing.assert_frame_equal(X_train_1.reset_index(drop=True), X_train_2.reset_index(drop=True))


# ---------------------------------------------------------------------------
# Tests for train_model
# ---------------------------------------------------------------------------

def test_train_model_returns_model(preprocessed_data):
    X_train, _, y_train, _ = app.split_data(preprocessed_data, "Fraudulent")
    model = app.train_model(X_train, y_train)
    assert model is not None


def test_train_model_has_predict(preprocessed_data):
    X_train, _, y_train, _ = app.split_data(preprocessed_data, "Fraudulent")
    model = app.train_model(X_train, y_train)
    assert hasattr(model, "predict")


def test_train_model_predict_shape(preprocessed_data):
    X_train, X_test, y_train, _ = app.split_data(preprocessed_data, "Fraudulent")
    model = app.train_model(X_train, y_train)
    predictions = model.predict(X_test)
    assert len(predictions) == len(X_test)


# ---------------------------------------------------------------------------
# Tests for save_model and loading it back
# ---------------------------------------------------------------------------

def test_save_model_creates_file(tmp_path, preprocessed_data):
    X_train, _, y_train, _ = app.split_data(preprocessed_data, "Fraudulent")
    model = app.train_model(X_train, y_train)
    model_path = str(tmp_path / "model.pkl")

    app.save_model(model, model_path)

    assert os.path.exists(model_path)


def test_save_model_can_be_loaded(tmp_path, preprocessed_data):
    X_train, X_test, y_train, _ = app.split_data(preprocessed_data, "Fraudulent")
    model = app.train_model(X_train, y_train)
    model_path = str(tmp_path / "model.pkl")

    app.save_model(model, model_path)
    loaded_model = joblib.load(model_path)

    assert hasattr(loaded_model, "predict")
    # Loaded model should produce the same predictions as the original
    np.testing.assert_array_equal(model.predict(X_test), loaded_model.predict(X_test))


# ---------------------------------------------------------------------------
# Tests for test_model
# ---------------------------------------------------------------------------

def test_test_model_returns_float(preprocessed_data):
    X_train, X_test, y_train, y_test = app.split_data(preprocessed_data, "Fraudulent")
    model = app.train_model(X_train, y_train)
    score = app.test_model(model, X_test, y_test)
    assert isinstance(score, float)


def test_test_model_score_in_valid_range(preprocessed_data):
    X_train, X_test, y_train, y_test = app.split_data(preprocessed_data, "Fraudulent")
    model = app.train_model(X_train, y_train)
    score = app.test_model(model, X_test, y_test)
    assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# Integration / end-to-end tests (original tests preserved)
# ---------------------------------------------------------------------------

def test():
    assert True


def test_model_file_created():
    app.main()  # Assuming the main function encapsulates the training logic
    assert os.path.exists('models/model.pkl')


def test_model_score():
    score = app.main()  # Assuming the main function returns the score
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0

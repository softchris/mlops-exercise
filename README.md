# Exercise - understanding MLOps using GitHub Actions

## Requirements

- A GitHub account.
- Basic knowledge of Python.
- Python installed on your machine.

## Problem Statement

You have a python script or Notebook and you want to ensure that any changes made to the script or notebook are automatically tested so that you can ensure that the changes do not break the code or worsens the performance of the model.

## Theory

What's a GitHub Action?

GitHub Actions help you automate tasks within your software development life cycle. GitHub Actions are event-driven, meaning that you can run a series of commands after a specified event has occurred. For example, every time someone creates a pull request for a repository, you can automatically run a command that executes a software testing script.

What's a workflow?

A workflow is a configurable automated process made up of one or more jobs. You must create a YAML file to define your workflow configuration. The file must be stored in the `.github/workflows` directory of your repository.

Example of a workflow file:

```yaml
name: Manually triggered workflow
on: 
  workflow_dispatch:
  
jobs:
  check-bats-version:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '14'
      - run: npm install -g bats
      - run: bats -v
```

The above workflow file is triggered manually (`workflow_dispatch`).

- It defines a job called `check-bats-version` that runs on the latest version of Ubuntu.
- It defines a series of steps that the job should take:
  - Checks out the repository.
  - Sets up Node.js version 14.
  - Installs `bats` (Bash Automated Testing System) globally.
  - Runs the `bats -v` command to check the version of `bats`.

## Assignment

In this assignment, we'll set up a workflow that runs a test script whenever a push is made to the repository. The test script will test the performance of a model that predicts whether a credit card transaction is fraudulent or not.

### Step 0 (optional, if you want to test the code locally)

In this steps, you'll try to run the code and the tests. It would therefore require you to have the following installed on your machine:

- Python

1. Clone/Fork this repository to your GitHub account.

1. Start the project by creating a virtual environment and install dependencies:

    ```bash
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

    For Windows users:

    ```bash
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```

1. Generate a random dataset using the following code:

    ```python
    python util/generate.py
    
    ```

    This command stores credit_card_records.csv in the data folder.

1. Run the app using the following command:

    ```bash
    python app.py
    ```

    It should output the following:

    ```bash
    Model accuracy: <some value between  and 1>
    ```

1. Run the tests using the following command, using `pytest`:

    ```bash
    pytest
    ```

    It should output the following:

    ```bash
    .
    ----------------------------------------------------------------------
    Ran 2 tests in 0.000s

    OK
    ```

### Step 1 - your first workflow

The object of this step is to get your first feel for what it's like to have GitHub Actions automate things for you.

1. Create a workflow file that runs the test script whenever you choose to run it manually.

    Copy the file `solution/workflows/manual.yml` to `.github/workflows/manual.yml`.

    Run the workflow by going to your repo on GitHub, clicking on the `Actions` tab, and then clicking on the `Run workflow` button.

    You should see the workflow running and bats version being printed in the logs.

**What did you learn?**

You've learned how the GitHub Actions platform works and how to create a workflow that runs on demand. Next, we'll apply GitHub Actions to our specific use case.

### Step 2 - run the tests on new pull request

A common way of working is to create a new branch for a new feature or bug fix, make the changes, and then create a pull request to merge the changes into the main branch. This way of working gives your colleagues a chance to review your code before it's merged.

Here's a great opportunity to let a GitHub Action run the tests for you whenever a new pull request is created. A failed test means you've introduced a bug or worsened the performance of the model.

1. Copy the file `solution/workflows/pull_request.yml` to `.github/workflows/pull_request.yml`.

    Let's examine why this works:

    ```yml
    on:
      pull_request:
        types: [opened, reopened]
    ```

    The above code listens for pull requests that are opened or reopened and runs the job `check_code` if so.

    Inspecting the job, we see the following definition:

    ```yml
     runs-on: ubuntu-latest
        steps:
        - uses: actions/checkout@v4
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.x'
        - name: Install dependencies
          run: |
            python -m pip install --upgrade pip
            pip install -r requirements.txt
        - name: Test with pytest
          run: |
            pip install pytest pytest-cov
            pytest tests.py --doctest-modules --junitxml=junit/test-results.xml --cov=com --cov-report=xml --cov-report=html
    ```

    Here's what the job does:

    - It runs on the latest version of Ubuntu.
    - It checks out the repository.
    - It sets up Python 3.x.
    - It installs dependencies.
    - It runs the tests using `pytest`.

**What did you learn?**

If the test fails, the pull request will indicate so, this is a great way to signal that this code should not be merged into the main branch as it would break the code or worsen the performance of the model.

### Step 3 (optional) - compare the performance of the model

So far, our tests look like so:

```python
def test_model_file_created():
    app.main()  # Assuming the main function encapsulates the training logic
    assert os.path.exists('models/model.pkl')

def test_model_score():
    score = app.main()  # Assuming the main function returns the score
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
```

These tests are great for ensuring the model is created and that the score is within a certain range. However, they don't test the performance of the model versus earlier version of the model. So how can we introduce such a mechanism?

One way to do this is to:

- Store the score of the model in a file. Such a file could look like so:

    ```json
    [{
        "version": "1.0",
        "score": 0.8
    },
    {
        "version": "1.1",
        "score": 0.04
    }]
    ```

    Here we see that the model is improving for each version. In the context of testing the model to see if we've improved the model or worsened it is to train the model and compare the score with the previous score, in this case, compare the score of version 1.1 with the current version you're working on.

Here's the changes we need to make to the tests:

1. Create a file called `model_scores.json` in the root of the project.

1. Add the following code to the test file, `tests.py`:

    ```python
    import json
    import os

    def test_model_score():
        score = app.main()  # Assuming the main function returns the score
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0

        # Load the model scores
        with open('model_scores.json', 'r') as f:
            model_scores = json.load(f)

        # Get the latest model score
        latest_score = model_scores[-1]['score']

        # Compare the latest score with the current score
        assert score >= latest_score
    ```

    Now, we've added a test that compares the latest score with the current score. If the current score is worse than the latest score, the test will fail.

    > NOTE: if the tests pass, you will see that in the PR, add a new entry if so to the JSON file like so:

    ```json
    {
        "version": "1.2",
        "score": <new score>
    }
    ```

    > TIP: it's a good idea if you're a developer to tag this commit with a version number, e.g., `v1.2` like so: `git tag v1.2` and then push the tag to GitHub like so: `git push origin v1.2`. This way, you can easily find where in your code the model was improved or worsened.

**What did you learn?**

You've learned how to compare the performance of the model with the previous version of the model. This is a great way to ensure that the model is improving and not worsening.

## Hand in

Send a link to your repository on GitHub to your teacher.
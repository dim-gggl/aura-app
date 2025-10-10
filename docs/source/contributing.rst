Contributing Guide
===================

Thank you for your interest in contributing to Aura Art! This guide will help you get started.

Getting Started
---------------

Development Setup
~~~~~~~~~~~~~~~~~

1. Fork the repository on GitHub
2. Clone your fork locally:

   .. code-block:: bash

      git clone https://github.com/your-username/aura-app.git
      cd aura-app

3. Create a virtual environment:

   .. code-block:: bash

      python -m venv .venv
      source .venv/bin/activate  # On Windows: .venv\Scripts\activate

4. Install dependencies:

   .. code-block:: bash

      uv sync

5. Set up the development environment:

   .. code-block:: bash

      cp env.example .env
      python manage.py migrate
      python manage.py createsuperuser

6. Start the development server:

   .. code-block:: bash

      python manage.py runserver

Code Style
----------

Python Style
~~~~~~~~~~~~

We follow PEP 8 style guidelines:

* Use 4 spaces for indentation
* Maximum line length of 88 characters
* Use meaningful variable and function names
* Write docstrings for all functions and classes

Django Conventions
~~~~~~~~~~~~~~~~~~

Follow Django best practices:

* Use Django's built-in functionality when possible
* Write tests for new features
* Use Django's form handling
* Follow the MTV (Model-Template-View) pattern

Documentation
~~~~~~~~~~~~~

* Write docstrings in English
* Include type hints where appropriate
* Document complex business logic
* Update this documentation when adding new features

Testing
-------

Running Tests
~~~~~~~~~~~~~

Run the test suite:

.. code-block:: bash

   python manage.py test

Run specific test modules:

.. code-block:: bash

   python manage.py test artworks.tests
   python manage.py test contacts.tests

Run with coverage:

.. code-block:: bash

   coverage run --source='.' manage.py test
   coverage report
   coverage html

Writing Tests
~~~~~~~~~~~~~

Write tests for:

* Model methods and properties
* View functionality
* Form validation
* API endpoints
* Business logic

Test Structure
~~~~~~~~~~~~~~

Organize tests in the following structure:

.. code-block:: python

   class TestArtworkModel(TestCase):
       def setUp(self):
           """Set up test data."""
           self.artist = Artist.objects.create(name="Test Artist")
           self.artwork = Artwork.objects.create(
               title="Test Artwork",
               artist=self.artist
           )

       def test_artwork_str_representation(self):
           """Test artwork string representation."""
           self.assertEqual(str(self.artwork), "Test Artwork")

       def test_artwork_get_absolute_url(self):
           """Test artwork absolute URL."""
           expected_url = f"/artworks/{self.artwork.id}/"
           self.assertEqual(self.artwork.get_absolute_url(), expected_url)

Pull Request Process
--------------------

Creating a Pull Request
~~~~~~~~~~~~~~~~~~~~~~~

1. Create a feature branch:

   .. code-block:: bash

      git checkout -b feature/your-feature-name

2. Make your changes and commit:

   .. code-block:: bash

      git add .
      git commit -m "Add your feature description"

3. Push to your fork:

   .. code-block:: bash

      git push origin feature/your-feature-name

4. Create a pull request on GitHub

Pull Request Guidelines
~~~~~~~~~~~~~~~~~~~~~~~

* Write clear, descriptive commit messages
* Include tests for new functionality
* Update documentation as needed
* Ensure all tests pass
* Follow the existing code style

Commit Message Format
~~~~~~~~~~~~~~~~~~~~~

Use the following format for commit messages:

.. code-block::

   type(scope): description

   Optional longer description

   Closes #issue-number

Types:
* ``feat``: New feature
* ``fix``: Bug fix
* ``docs``: Documentation changes
* ``style``: Code style changes
* ``refactor``: Code refactoring
* ``test``: Test additions or changes
* ``chore``: Maintenance tasks

Examples:

.. code-block::

   feat(artworks): add artwork search functionality

   Implement full-text search for artworks by title, artist, and medium.
   Includes search highlighting and result ranking.

   Closes #123

   fix(api): resolve pagination issue in artwork list

   Fix incorrect page count calculation in artwork list API endpoint.

   Closes #456

Issue Reporting
---------------

Bug Reports
~~~~~~~~~~~

When reporting bugs, include:

* Description of the problem
* Steps to reproduce
* Expected behavior
* Actual behavior
* Environment details (OS, Python version, etc.)
* Screenshots if applicable

Feature Requests
~~~~~~~~~~~~~~~~

When requesting features, include:

* Description of the feature
* Use case and motivation
* Proposed implementation approach
* Any alternatives considered

Development Workflow
--------------------

Branch Naming
~~~~~~~~~~~~~

Use descriptive branch names:

* ``feature/artwork-search``
* ``fix/pagination-bug``
* ``docs/api-documentation``
* ``refactor/user-authentication``

Code Review Process
~~~~~~~~~~~~~~~~~~~

1. All pull requests require review
2. Address review comments promptly
3. Make requested changes in new commits
4. Squash commits before merging if requested

Release Process
---------------

Version Numbering
~~~~~~~~~~~~~~~~~

We use semantic versioning (MAJOR.MINOR.PATCH):

* **MAJOR**: Breaking changes
* **MINOR**: New features (backward compatible)
* **PATCH**: Bug fixes (backward compatible)

Release Checklist
~~~~~~~~~~~~~~~~~

Before releasing:

* [ ] Update version numbers
* [ ] Update CHANGELOG.md
* [ ] Run full test suite
* [ ] Update documentation
* [ ] Create release notes
* [ ] Tag the release

Community Guidelines
--------------------

Code of Conduct
~~~~~~~~~~~~~~~

* Be respectful and inclusive
* Welcome newcomers and help them learn
* Focus on constructive feedback
* Respect different opinions and approaches

Getting Help
~~~~~~~~~~~~

* Check existing issues and pull requests
* Ask questions in discussions
* Join our community chat
* Contact maintainers directly for urgent issues

Recognition
-----------

Contributors
~~~~~~~~~~~~

We recognize contributors in:

* README.md contributors section
* Release notes
* Project documentation
* Annual contributor highlights

Types of Contributions
~~~~~~~~~~~~~~~~~~~~~~

We welcome various types of contributions:

* Code contributions
* Documentation improvements
* Bug reports
* Feature requests
* Testing and quality assurance
* Design and user experience
* Community support

Thank you for contributing to Aura Art!

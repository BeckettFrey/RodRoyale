test:
	python -m venv venv && source venv/bin/activate && \
	pip install -r requirements.txt && \
	pip install -r requirements-dev.txt && \
	pip install pytest pytest-cov && \
	export MONGODB_URI="mongodb://localhost:27017/testdb" && \
	pytest --cov=. --cov-report=term-missing --disable-warnings --tb=short

# Local
run:
	streamlit run app.py

docker_build_local:
	docker build --tag=grid-intelligence-frontend:local .

docker_run_local:
	docker run \
		-e PORT=8080 -p 8080:8080 \
		grid-intelligence-frontend:local

run:
	streamlit run app.py

format:
	black streamlit-web/

web:
	streamlit run streamlit-web/src/app.py

backend:
	fastapi run backend.py


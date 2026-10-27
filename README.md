# AI Based Smart Traffic Signal Optimization

Adaptive signal timing for a 4-way intersection using classical computer vision and evolutionary + fuzzy AI. No trained models, no datasets.

## Pipeline
1. **Perception** – OpenCV MOG2 background subtraction → noise filtering → contour filter → vehicle count per lane.
2. **Optimization** – genetic algorithm finds green times minimizing total waiting time.
3. **Control** – fuzzy logic adjusts green time from density and growth.
4. **Safety rules** – min/max green, yellow + all-red, starvation cap, emergency priority.
5. **UI** – counts or videos in, signal plan + live signal simulation out.

## Run locally
```bash
pip install -r requirements.txt
python app.py        # http://localhost:5000
python controller.py # CLI test
```

## API
- `POST /plan` – `{"counts":[a,b,c,d], "prev":[...], "emergency_lane":0-3}`
- `POST /analyze` – form-data `video0..video3`, optional `emergency_lane`, `prev`
- `GET /health`

## Deploy
- **Vercel:** works for the UI and `/plan` (manual counts). Video upload is limited to 4.5 MB there.
- **Render / Railway (full features):** build `pip install -r requirements.txt`, start `gunicorn app:app --timeout 120`.

## Files
`counter.py` CV counting · `ga.py` genetic algorithm · `fuzzy.py` fuzzy rules · `controller.py` plan + safety rules · `config.py` settings

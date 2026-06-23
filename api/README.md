# API

This directory contains the FastAPI backend for serving the Scout ranking engine as a live service. 

It exposes endpoints such as `/rank-candidates` to allow the recruiter dashboard (or other external tools) to submit job descriptions and retrieve ranked candidates in real time. The API directly integrates with the logic in the `scout/pipeline` package.

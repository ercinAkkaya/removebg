from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from rembg import remove, new_session
import uvicorn

app = FastAPI(title="Background Removal Service")

# -----------------------------------------------------------------------------
# GLOBAL SCOPE INITIALIZATION
# -----------------------------------------------------------------------------
# CRITICAL: We initialize the session here so the model is loaded ONLY ONCE 
# when the container starts. This prevents reloading the ~170MB model on every request,
# which would drastically hurt performance and cause timeouts on Cloud Run.
model_name = "birefnet-general"
print(f"Initializing rembg session with model: {model_name}...")
session = new_session(model_name)
print("Rembg session initialized successfully.")

@app.post("/remove-bg")
async def remove_bg(file: UploadFile = File(...)):
    """
    Endpoint to remove background from an uploaded image.
    Returns the processed image directly as a PNG response.
    """
    # Read the uploaded file as bytes
    input_data = await file.read()
    
    # Process the image using the pre-initialized global session
    # rembg.remove accepts bytes and returns bytes (PNG) by default when input is bytes
    output_data = remove(input_data, session=session)
    
    # Return the binary data directly with the correct media type
    return Response(content=output_data, media_type="image/png")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

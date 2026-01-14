from fastapi import FastAPI, UploadFile, File
from fastapi.responses import Response
from rembg import remove, new_session
import uvicorn
import onnxruntime as ort

app = FastAPI(title="Background Removal Service")

# -----------------------------------------------------------------------------
# GLOBAL SCOPE INITIALIZATION
# -----------------------------------------------------------------------------
# CRITICAL: We initialize the session here so the model is loaded ONLY ONCE 
# when the container starts. This prevents reloading the ~170MB model on every request,
# which would drastically hurt performance and cause timeouts on Cloud Run.
import onnxruntime as ort
from rembg import remove, new_session

# CONFIG: Memory Optimization for Cloud Run
sess_opts = ort.SessionOptions()
sess_opts.intra_op_num_threads = 1
sess_opts.inter_op_num_threads = 1
# Disable memory arena to prevent pre-allocation of huge chunks
sess_opts.enable_cpu_mem_arena = False 
# Optional: Graph optimization reduces memory usage slightly
sess_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_BASIC

model_name = "birefnet-general"
print(f"Initializing rembg session with model: {model_name}...")
# Pass the custom session options
session = new_session(model_name, providers=["CPUExecutionProvider"], session_options=sess_opts)
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

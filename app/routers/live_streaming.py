from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from fastapi.responses import StreamingResponse
import cv2
import numpy as np

router = APIRouter()

@router.websocket("/ws/live_stream")
async def live_stream(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket connection established")

    try:
        while True:
            # Receive the video frame as a binary WebSocket message
            frame = await websocket.receive_bytes()

            # Convert the binary data into a numpy array
            np_arr = np.frombuffer(frame, dtype=np.uint8)
            img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)  # Decode as an image

            if img is None:
                continue  # If the frame is not valid, skip it

            # Process the frame (optional: apply some image processing)
            # For example, convert to grayscale
            gray_frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Optionally, you can save or send processed frames to clients
            # For simplicity, let's just show the frame (for testing purposes)
            cv2.imshow("Received Frame", gray_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Exit on 'q' key press
                break

    except WebSocketDisconnect:
        print("Client disconnected")
    finally:
        cv2.destroyAllWindows()


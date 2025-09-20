// src/features/webcam-drawing/CanvasHost.jsx
import React, { useRef, useEffect } from 'react';
import Webcam from 'react-webcam';
import * as tf from '@tensorflow/tfjs';
import * as handpose from '@tensorflow-models/handpose';
import '@tensorflow/tfjs-backend-webgl'; // Import this for WebGL backend
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';
import { Hands, HAND_CONNECTIONS } from '@mediapipe/hands';

export default function CanvasHost() {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);
  const handsRef = useRef(null);
  const pointsRef = useRef([]);

  useEffect(() => {
    const runHandpose = async () => {
      // Use the WebGL backend
      await tf.setBackend('webgl'); 
      console.log('Using WebGL backend:', tf.getBackend());

      const video = webcamRef.current.video;
      if (!video) return;

      const hands = new Hands({
        locateFile: (file) =>
          `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`,
      });
      hands.setOptions({
        modelComplexity: 1,
        maxNumHands: 1,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });
      hands.onResults(onResults);
      handsRef.current = hands;

      video.addEventListener('loadeddata', () => {
        const videoWidth = video.videoWidth;
        const videoHeight = video.videoHeight;
        video.width = videoWidth;
        video.height = videoHeight;
        canvasRef.current.width = videoWidth;
        canvasRef.current.height = videoHeight;
      });

      const sendToHands = async () => {
        if (!video.paused && !video.ended) {
          await hands.send({ image: video });
        }
        requestAnimationFrame(sendToHands);
      };
      sendToHands();
    };

    runHandpose();

    return () => {
      if (handsRef.current) {
        handsRef.current.close();
      }
    };
  }, []);

  const onResults = (results) => {
    const video = webcamRef.current.video;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');

    if (!video || !canvas || !ctx) {
      return;
    }

    ctx.save();
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.scale(-1, 1);
    ctx.translate(-canvas.width, 0);
    ctx.drawImage(results.image, 0, 0, canvas.width, canvas.height);

    if (results.multiHandLandmarks) {
      for (const landmarks of results.multiHandLandmarks) {
        // Draw the hand skeleton
        drawConnectors(ctx, landmarks, HAND_CONNECTIONS, {
          color: '#00FF00',
          lineWidth: 5,
        });

        // Get the tip of the index finger (point 8)
        const indexFingerTip = landmarks[8];
        const { x, y } = indexFingerTip;
        const canvasX = x * canvas.width;
        const canvasY = y * canvas.height;

        // Draw a circle at the tip of the index finger
        ctx.beginPath();
        ctx.arc(canvasX, canvasY, 10, 0, 2 * Math.PI);
        ctx.fillStyle = 'red';
        ctx.fill();

        // Add the point to our drawing history
        pointsRef.current.push({ x: canvasX, y: canvasY });
      }
    }

    // Draw the continuous line
    if (pointsRef.current.length > 1) {
      ctx.beginPath();
      ctx.moveTo(pointsRef.current[0].x, pointsRef.current[0].y);
      for (let i = 1; i < pointsRef.current.length; i++) {
        ctx.lineTo(pointsRef.current[i].x, pointsRef.current[i].y);
      }
      ctx.strokeStyle = 'blue';
      ctx.lineWidth = 5;
      ctx.stroke();
    }
    
    ctx.restore();
  };

  return (
    <div style={{ position: 'relative' }}>
      <Webcam
        ref={webcamRef}
        style={{
          position: 'absolute',
          marginLeft: 'auto',
          marginRight: 'auto',
          left: 0,
          right: 0,
          textAlign: 'center',
          zindex: 9,
          width: 640,
          height: 480,
          visibility: 'hidden',
        }}
      />
      <canvas
        ref={canvasRef}
        style={{
          position: 'absolute',
          marginLeft: 'auto',
          marginRight: 'auto',
          left: 0,
          right: 0,
          textAlign: 'center',
          zindex: 10,
          width: 640,
          height: 480,
        }}
      />
    </div>
  );
}
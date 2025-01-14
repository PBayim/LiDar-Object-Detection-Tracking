# Recap of my understanding about this task 

## Kew words
- Detect and track :
    - surrounding traffic (moving cars)
    - (crossing) pedestrians 

- Tasks 
    - The review of the sensor's specification and the alignment with common requirements for self-driving cars
    - A first assessment and sanity check of data 
    - The development of the object detection and object tracking algorithm

- Point clouds data constitution
    - range and bearing information
    - sensor is placed at a fixed position (the origin) 

- Matters Out of scope
    - Develop the final algorithm for deployment onthe processing computer
    - Narrow our approach by considering the real-time requirements

- Success requirements 
    - Develop an algorithm, which fulfils the task for verification and validation
    - The desired performance for our approach is a correct classification rate of 0.99 and a false alarm
rate of 0.01 per hour.
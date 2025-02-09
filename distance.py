import RPi.GPIO as GPIO
import time
import ollama  # Import Ollama AI

GPIO.setmode(GPIO.BCM)    # Set GPIO pin numbering
GPIO.setwarnings(False)  # Disable warnings

TRIG = 23   # GPIO23
ECHO = 24   # GPIO24
SERVO_PIN = 15  # GPIO 15 (Pin 10)


def distance():
    """Measures distance using the ultrasonic sensor."""
    GPIO.setup(TRIG, GPIO.OUT)  # Set TRIG as OUTPUT
    GPIO.setup(ECHO, GPIO.IN)   # Set ECHO as INPUT
    GPIO.output(TRIG, False)    # Set TRIG as LOW

    time.sleep(1)   # Delay of 1 second

    GPIO.output(TRIG, True)  # Set TRIG as HIGH
    time.sleep(0.00001)  # Delay of 0.00001 seconds
    GPIO.output(TRIG, False) # Set TRIG as LOW  

    while   GPIO.input(ECHO) == 0:  # Check if ECHO is LOW
        start = time.time() # Save the start time
        
    while   GPIO.input(ECHO) == 1:  # Check if ECHO is HIGH
        stop = time.time()  # Save the stop time
        
    duration = stop - start    # Calculate the duration of the signal
    distance = (duration * 17150)  # Calculate the distance
    distance = round(distance, 2)   # Round the distance to 2 decimal places

    return distance

def servo_CONTROL():
    """Initializes and returns a function to set the servo angle."""
    GPIO.setup(SERVO_PIN, GPIO.OUT)
    pwm = GPIO.PWM(SERVO_PIN, 50)
    pwm.start(7.5)  # Neutral position (90 degrees)

    def set_angle(angle):
        """Moves the servo to the specified angle."""
        duty = (angle / 18) + 2.5  # Convert angle to duty cycle
        GPIO.output(SERVO_PIN, True)
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.5)
        GPIO.output(SERVO_PIN, False)
        pwm.ChangeDutyCycle(0)

    return set_angle

def process_distance(dist):
    """Sends distance to Ollama AI and retrieves the recommended servo angle."""
    try:
        response = ollama.chat(
            model="llama3.2:1b",  # Replace with your Ollama model name
            messages=[{"role": "user", "content": f"What angle should the servo move for {dist} cm?"}]
        )
        angle = int(response['message']['content'].strip())  # Convert response to integer
        return angle if 0 <= angle <= 180 else 90  # Ensure valid angle range
    except Exception as e:
        print(f"AI Model Error: {e}")
        return 90  # Default to 90° if AI fails


def main():
    """Main function to read distance and control servo movement."""
    set_angle = servo_CONTROL() # Create an instance of the servo_CONTROL function  

    try:
        while True:    # Loop to run the distance measurement

            print("Measuring distance...")  # Print message
            dist = distance()
            print("Distance:", dist, "cm")  # Print the distance

            # Get AI-determined servo angle
            angle = process_distance(dist)
            print(f"AI model decided: Moving servo to {angle}°")

            set_angle(angle)  # Move the servo

            # if dist < 10:
            #     print("Distance less than 10cm, moving servo to 0Â°")
            #     set_angle(0)
            # elif (dist < 20 and  dist > 10):
            #     print("Distance less than 20cm, moving servo to 45Â°")
            #     set_angle(45)
            # elif (dist < 30 and dist > 20):
            #     print("Distance greater than 20cm, moving servo to 90Â°")
            #     set_angle(90)
            # elif (dist < 40 and dist > 30):
            #     print("Distance greater than 30cm, moving servo to 135Â°")
            #     set_angle(135)
            # else:
            #     print("Distance greater than 40cm, moving servo to 180Â°")
            #     set_angle(180)

            time.sleep(0.1)  # Add a small delay to avoid excessive CPU usage

    except KeyboardInterrupt:
        print("Stopping...")
        GPIO.cleanup()


if __name__ == "__main__": 
    main()  # Run the main function
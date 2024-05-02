import cv2

def detect_faces(image_path):
    # Load the image
    image = cv2.imread(image_path)
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Load the pre-trained face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    # Detect faces in the image
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces

def crop_faces(image_path, faces):
    # Load the image
    image = cv2.imread(image_path)
    # Iterate over each face and crop it
    cropped_faces = []
    for (x, y, w, h) in faces:
        cropped_face = image[y:y+h, x:x+w]
        cropped_faces.append(cropped_face)
    return cropped_faces

def combine_faces(cropped_faces):
    # Find the maximum height among all cropped faces
    max_height = max(face.shape[0] for face in cropped_faces)
    # Resize all cropped faces to have the same height
    resized_faces = [cv2.resize(face, (int(face.shape[1] * max_height / face.shape[0]), max_height)) for face in cropped_faces]
    # Combine the resized faces horizontally
    combined_image = cv2.vconcat(resized_faces)
    return combined_image

def main():
    # image_path = 'image_with_faces.jpg'  # Replace 'image_with_faces.jpg' with the path to your image
    # faces = detect_faces(image_path)
    # if len(faces) >= 2:
    #     cropped_faces = crop_faces(image_path, faces)
    #     combined_image = combine_faces(cropped_faces)
    #     cv2.imshow('Combined Faces', combined_image)
    #     cv2.waitKey(0)
    #     cv2.destroyAllWindows()
    # else:
    #     print("Not enough faces detected.")

    import common
    import storageGoogle

    print(storageGoogle.file_exists('input_video.mp4'))

if __name__ == "__main__":
    main()
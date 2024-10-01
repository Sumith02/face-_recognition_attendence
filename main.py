import sys
import os
from PIL import Image
import cv2
import wand.image

def get_image_name():
    return input("Enter the image name (e.g., 1.png): ")

def get_processed_image_name():
    return input("Enter the name for the processed image (e.g., processed.jpg): ")

def get_process_choice():
    print("Choose the process you want to perform:")
    print("1: Compress the image")
    print("2: Convert the image to black and white")
    print("3: Both compress and convert to black and white")
    choice = input("Enter your choice (1/2/3): ")
    return choice

def check_file_existence(file_path, file_description):
    if not os.path.exists(file_path):
        print(f"{file_description} not found at {file_path}.")
        sys.exit(1)

def read_threshold_value(file_path):
    with open(file_path) as f:
        return int(f.read().strip())

def convert_to_black_and_white(input_image_path, threshold_value, output_image_path):
    image = cv2.imread(input_image_path)
    name = os.path.basename(input_image_path)
    print(f"Processing {name}")

    # Get the Image DPI value from the Input image
    image_pil = Image.open(input_image_path)
    dpi_value = image_pil.info.get('dpi', (72, 72))[0]  # Default to 72 if dpi info is not available
    compression_type = image_pil.info.get('compression', 'tiff_deflate')  # Default compression

    # Convert to Grayscale format
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply threshold
    _, black_and_white_image = cv2.threshold(gray_image, threshold_value, 255, cv2.THRESH_BINARY)
    bw_image_pil = Image.fromarray(black_and_white_image)

    # Convert to Black & White Mode
    bw_image = bw_image_pil.convert('1')
    temp_output_path = os.path.join(input_directory, f"temp_{name}")

    bw_image.save(temp_output_path, dpi=(dpi_value, dpi_value), compression=compression_type)

    # Convert to TIFF version 5.0 using ImageMagick if the image is TIFF
    if name.lower().endswith('.tif'):
        with wand.image.Image(filename=temp_output_path) as img:
            img.save(filename=output_image_path)
        os.remove(temp_output_path)
    else:
        if os.path.exists(output_image_path):
            os.remove(output_image_path)
        os.rename(temp_output_path, output_image_path)

    return output_image_path

def compress_image(input_image_path, quality, output_image_path):
    try:
        image = cv2.imread(input_image_path)
        
        if image is None:
            print(f"Error: Unable to read image {input_image_path}.")
            return

        compression_params = [cv2.IMWRITE_JPEG_QUALITY, quality]
        success = cv2.imwrite(output_image_path, image, compression_params)

        if not success:
            print(f"Error: Failed to save compressed image as {output_image_path}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    global input_directory
    input_directory = "C://Users//sumit//cgMiniProject//images"
    value_ini_path = "value.ini"
    
    print("\nTIF, PNG: Black & White mode Conversion and Compression\n")

    image_name = get_image_name()
    input_image_path = os.path.join(input_directory, image_name)
    processed_image_name = get_processed_image_name()
    output_image_path = os.path.join(input_directory, processed_image_name)

    check_file_existence(input_image_path, "Image")
    check_file_existence(value_ini_path, "value.ini file")

    process_choice = get_process_choice()

    if process_choice == '1':
        quality = input("Enter the desired quality (1-100, where 100 is best quality): ")
        try:
            quality = int(quality)
            if quality < 1 or quality > 100:
                print("Quality should be between 1 and 100. Using default value of 90.")
                quality = 90
        except ValueError:
            print("Invalid quality value. Using default value of 90.")
            quality = 90
        compress_image(input_image_path, quality, output_image_path)
        print(f"The image has been compressed and saved as {processed_image_name}")
    elif process_choice == '2':
        threshold_value = read_threshold_value(value_ini_path)
        convert_to_black_and_white(input_image_path, threshold_value, output_image_path)
        print(f"The image has been converted to black and white and saved as {processed_image_name}")
    elif process_choice == '3':
        threshold_value = read_threshold_value(value_ini_path)
        bw_image_path = convert_to_black_and_white(input_image_path, threshold_value, output_image_path)
        quality = input("Enter the desired quality (1-100, where 100 is best quality): ")
        try:
            quality = int(quality)
            if quality < 1 or quality > 100:
                print("Quality should be between 1 and 100. Using default value of 90.")
                quality = 90
        except ValueError:
            print("Invalid quality value. Using default value of 90.")
            quality = 90
        compress_image(bw_image_path, quality, output_image_path)
        print(f"The image has been compressed and converted to black and white and saved as {processed_image_name}")
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

    print("\n\n*** Process Completed ***\n")

if __name__ == "__main__":
    main()

from matplotlib import pyplot as plt
from PIL import Image
from os import path, makedirs
from easyocr import Reader

import cv2
import numpy as np
from imutils import grab_contours


def edit_photo(img_source):
    """
        Редактирование фотографии - скрытие номера автомобиля и наложение водяного знака
        Возвращает True если найден (текст) номера авто
    """

    print(f"\n\n------------------SELECTED NEW photo --> {img_source}")
    current_path = path.dirname(path.abspath(__file__))  # C:\Users\tansh\selenium_course\car_hide

    white = (255, 255, 255)
    black = (0, 0, 0)
    font = cv2.FONT_HERSHEY_SIMPLEX

    img = cv2.imread(img_source)

    im = Image.open(img_source)
    width, height = im.size
    print("WIDTH AND HEIGHT of photo: ", width, height)
    im.close()

    def fill_car_number_and_org_name(left_top_x_coord, left_top_y_coord, right_bottom_x_coord, right_bottom_y_coord):
        """
            Функция закрашивает область номера авто по заданным координатам в белый прямоугольник (заливка)
            и наносит текст организации
        """
        start_point = tuple([left_top_x_coord, left_top_y_coord])
        end_point = tuple([right_bottom_x_coord, right_bottom_y_coord])
        print("Start and end points:", start_point, end_point)

        x_coord_module = right_bottom_x_coord - left_top_x_coord

        cv2.rectangle(img, start_point, end_point, white, -1)  # Заливка номерного знака
        cv2.rectangle(img, start_point, end_point, black, 2)  # Границы, черная рамка

        kick = (left_top_y_coord - right_bottom_y_coord) / 3 + right_bottom_y_coord
        now = right_bottom_y_coord * 0.98
        cv2.putText(img, text="COMPANY.KZ", org=(int(left_top_x_coord * 1.045), int(kick)),
                    fontFace=font, fontScale=x_coord_module / 225, color=black, thickness=2,
                    lineType=cv2.LINE_AA)  # Текст внутри

    def add_watermark():
        """
            Функция наносит водяной знак компании на правый нижний угол
        """
        cv2.putText(img, text="COMPANY.KZ", org=(int(width * 0.6), int(height * 0.96)), fontFace=font,
                    fontScale=width / 500, color=black, thickness=3, lineType=cv2.LINE_AA)  # Текст

    def save_image():
        """
            Функция сохраняет измененное изображение в папке edited_photos (относительный путь)
        """
        directory = current_path + "\edited_photos\\"

        if not path.exists(directory):
            makedirs(directory)

        print("EDITED PHOTO SAVE IN DIR", directory, img_source[16:])
        # убираем относительное положение, папку origin_photos из img_source, оставляем только имя картинки
        is_written = cv2.imwrite(directory + "hidden_" + img_source[16:], img)   # save matrix/array as image file
        print('Image is successfully saved as file.' if is_written else "Cannot save image")

        return is_written

    def try_get_car_number_text():
        """
            Функция пытается прочитать текст номерного знака автомобиля на фотографии
            Если на фото не найден текст, распозанет как:
                на фото не найден номер автомобиля
        """
        reader = Reader(['en'])
        result_text_array = reader.readtext(cropped_image)
        len_text_array = len(result_text_array)

        if len_text_array > 0:
            if len_text_array == 1:
                car_number_txt = result_text_array[0][-2]
            elif len_text_array == 2:
                car_number_txt = result_text_array[1][-2]
            else:
                print("Cannot get car number text", result_text_array, " --> LENGTH OF ARRAY: ", len_text_array)

            print("CAR NUMBER TEXT:", car_number_txt)
            return True

        return False

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    b_filter = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(b_filter, 30, 200)

    key_points = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = grab_contours(key_points)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    location = None
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 10, True)
        if len(approx) == 4:
            location = approx
            break

    mask = np.zeros(gray.shape, np.uint8)
    try:
        cv2.drawContours(mask, [location], 0, 255, -1)
        cv2.bitwise_and(img, img, mask=mask)
    except cv2.error:
        print("CANNOT READ TEXT  -> CAR NUMBER NOT FOUND")
        return False

    (x, y) = np.where(mask == 255)
    (x1, y1) = (np.min(x), np.min(y))
    (x2, y2) = (np.max(x), np.max(y))

    # Показать только номер автомобиля - со смещением 45 по наличию области/города
    cropped_image = gray[x1:x2 + 1, y1:y2 + 1]

    if try_get_car_number_text():

        # Левый верхний угол номера автомобиля
        left_top_x = approx[0][0][0]
        left_top_y = approx[0][0][1]

        # Правый нижний угол номера автомобиля
        right_bottom_x = round(1.08 * approx[2][0][0])  # Для покрытия номера области / города + 9% к длине
        right_bottom_y = (approx[2][0][1] + 3)  # Правая нижняя координата у

        fill_car_number_and_org_name(left_top_x, left_top_y, right_bottom_x, right_bottom_y)
        add_watermark()
        print(save_image())
        return True

    print("CAR NUMBER NOT FOUND")
    return False


if __name__ == '__main__':
    print("In file hide_car_number.py")
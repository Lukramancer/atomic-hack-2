from PIL import Image, ImageDraw, ImageFont

STANDARD_WIDTH, STANDARD_HEIGHT = 512, 512
INFO_HEIGHT, INFO_WIDTH = 64, 512


def generate_plots(
        image: Image,
        cls,
        boxes,
        confs,
        errors_map,
        line_width=5
):
    image = image.convert("RGBA")
    images = []

    width, height = image.size

    boxes[:, [0, 2]] *= width
    boxes[:, [1, 3]] *= height

    boxes = boxes.astype("int")

    for i, box in enumerate(boxes):
        half_side = max(box[2], box[3])
        left_border = max(0, box[0] - 2 * half_side)
        right_border = min(width, box[0] + 2 * half_side)
        top_border = max(0, box[1] - 2 * half_side)
        bottom_border = min(height, box[1] + 2 * half_side)

        cropped_image = image.crop((left_border, top_border, right_border, bottom_border))
        cropped_image = cropped_image.resize((STANDARD_WIDTH, STANDARD_HEIGHT))
        label = f"Дефект: {errors_map[cls[i]]['name']}"

        images.append([cropped_image, label])

    for i, box in enumerate(boxes):
        draw = ImageDraw.Draw(image)
        draw.rectangle(((box[0] - box[2] // 2, box[1] - box[3] // 2), (box[0] + box[2] // 2, box[1] + box[3] // 2)),
                       outline=errors_map[cls[i]]["rgb"], width=line_width)

    return image, images
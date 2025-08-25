import argparse
import cv2
import numpy as np
import torch
import matplotlib

from depth_anything_v2.dpt import DepthAnythingV2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Depth Anything V2 - Live Camera')
    parser.add_argument('--frame-width', type=int, default=256)
    parser.add_argument('--input-size', type=int, default=256)
    parser.add_argument('--encoder', type=str, default='vits', choices=['vits', 'vitb', 'vitl', 'vitg'])
    parser.add_argument('--pred-only', default='pred_only', dest='pred_only', action='store_true', help='only display the prediction')
    parser.add_argument('--grayscale', dest='grayscale', action='store_true', help='do not apply colorful palette')
    args = parser.parse_args()

    DEVICE = 'cuda' if torch.cuda.is_available() else \
             'mps' if torch.backends.mps.is_available() else 'cpu'

    model_configs = {
        'vits': {'encoder': 'vits', 'features': 64, 'out_channels': [48, 96, 192, 384]},
        'vitb': {'encoder': 'vitb', 'features': 128, 'out_channels': [96, 192, 384, 768]},
        'vitl': {'encoder': 'vitl', 'features': 256, 'out_channels': [256, 512, 1024, 1024]},
        'vitg': {'encoder': 'vitg', 'features': 384, 'out_channels': [1536, 1536, 1536, 1536]}
    }

    # Załaduj model
    depth_anything = DepthAnythingV2(**model_configs[args.encoder])
    depth_anything.load_state_dict(torch.load(
        f'checkpoints/depth_anything_v2_{args.encoder}.pth',
        map_location='cpu'
    ))
    depth_anything = depth_anything.to(DEVICE).eval()

    cmap = matplotlib.colormaps.get_cmap('Spectral_r')
    margin_width = 20

    # Otwórz kamerę (0 = domyślna)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Nie można otworzyć kamery")
        exit()

    while True:
        ret, frame = cap.read()
        frame = cv2.resize(frame, (args.frame_width, int(args.frame_width/4*3)))
        if not ret:
            print("Brak klatki z kamery")
            break

        # Inferencja głębi
        depth = depth_anything.infer_image(frame, args.input_size)
        depth = (depth - depth.min()) / (depth.max() - depth.min()) * 255.0
        depth = depth.astype(np.uint8)

        if args.grayscale:
            depth_vis = np.repeat(depth[..., np.newaxis], 3, axis=-1)
        else:
            depth_vis = (cmap(depth)[:, :, :3] * 255)[:, :, ::-1].astype(np.uint8)

        if args.pred_only:
            display_frame = depth_vis
        else:
            split_region = np.ones((frame.shape[0], margin_width, 3), dtype=np.uint8) * 255
            display_frame = cv2.hconcat([frame, split_region, depth_vis])

        # Pokaż w oknie
        cv2.imshow("Depth Anything V2 - Live", display_frame)

        # Wyjście po wciśnięciu 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

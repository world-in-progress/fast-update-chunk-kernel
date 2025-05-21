import argparse
from fast_update_chunk_kernel import Merger

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Grid Merger')
    parser.add_argument('--minio-endpoint', type=str, required=True, help='MinIO endpoint URL')
    parser.add_argument('--workspace-dir', type=str, required=True, help='Workspace directory')
    parser.add_argument('--description-path', type=str, required=True, help='Path to the description JSON file')
    parser.add_argument('--mp-num', type=int, default=4, help='Number of worker processes')
    args = parser.parse_args()

    merger = Merger(
        minio_endpoint=args.minio_endpoint,
        workspace_dir=args.workspace_dir,
        description_path=args.description_path,
        mp_num=args.mp_num
    )
    merger.run()

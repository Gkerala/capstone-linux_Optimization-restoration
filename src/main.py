import argparse
from src.optimizer import optimize_system
from src.restore import restore_system
from src.utils.logger import get_logger

logger = get_logger()

def main():
    parser = argparse.ArgumentParser(description="System Optimization and Restore Tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 최적화 서브 커맨드
    subparsers.add_parser("optimize", help="Run system optimization")

    # 복원 서브 커맨드
    subparsers.add_parser("restore", help="Run system restore")

    args = parser.parse_args()

    if args.command == "optimize":
        logger.info("Starting optimization...")
        optimize_system()  # 인자 없이 호출
        logger.info("Optimization finished successfully.")

    elif args.command == "restore":
        logger.info("Starting restore...")
        restore_system()  # 이 함수도 같은 방식이라면 인자 제거
        logger.info("Restore finished successfully.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()


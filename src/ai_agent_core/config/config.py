import argparse
from typing import Optional

def define_argparser():
    p = argparse.ArgumentParser()

    p.add_argument('--model_name', type=str, default='gpt-4o-mini',
                    help='사용할 LLM 모델 이름')
    p.add_argument('-t', '--temperature', type=float, default=.7,
                    help='답변 생성 시, 랜덤성을 결정하는 파라미터. 0 이상의 값을 가질 수 있습니다. 값이 클수록 확률적인(창의적인) 답변, 작을수록 결정적인 답변을 생성합니다. GPT-5 계열 모델은 지원하지 않습니다.')

    return p

# 안전하게 FastAPI에서 불러오는 함수
def load_config(args: Optional[list] = None):
    """
    FastAPI 내부에서 안전하게 config를 가져오기 위한 함수
    args=None → import 시 기본값 사용, CLI 인자는 무시
    """
    parser = define_argparser()
    if args is None:
        args = []
    return parser.parse_args(args)

if __name__ == "__main__":
    parser = define_argparser()
    config = parser.parse_args() 
    print("config:", config)
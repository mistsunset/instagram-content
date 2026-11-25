# instagram-content

Codex 대화에서 카드뉴스를 준비하고, Windsor.ai를 통해 승인받은 캐러셀을 `@mistsunset.lee`에 게시하는 저장소입니다. 대화에서 Codex에게 “`mistsunset/instagram-content`의 절차로 카드뉴스를 제작하고 캐러셀 승인 화면까지 준비해 줘”라고 요청하면 [운영 절차](AGENTS.md)를 사용할 수 있습니다.

게시용 이미지는 GitHub의 공개 원본 URL로 제공됩니다. 각각의 URL에는 커밋 SHA가 포함되어 검토한 이미지 버전이 고정됩니다. 캡션과 연결 자격 증명은 저장소에 올리지 않습니다. 별도 유료 서비스나 새 API 키 없이 기존 GitHub 및 Windsor.ai 연결을 사용합니다.

## 준비 스크립트

Python 3와 Pillow가 필요합니다. 카드 경로는 캐러셀에 표시할 순서대로 넘깁니다. 출력 폴더는 새 경로여야 합니다. 각 카드를 흰색 1080×1350 캔버스에 비율을 유지해 배치하고 JPEG로 저장합니다.

```sh
python scripts/prepare_carousel.py prepare --output /tmp/carousel-draft \
  --caption-file /tmp/caption.txt /tmp/card-one.png /tmp/card-two.png

python scripts/prepare_carousel.py payload --output /tmp/carousel-draft \
  --commit "$IMAGE_COMMIT_SHA" --batch-id "$BATCH_ID"
```

두 번째 명령은 GitHub에 업로드한 뒤 실행합니다. 출력 JSON은 `create_carousel_post`의 파라미터이며 그 자체로 게시를 실행하지 않습니다. 업로드와 게시 요청은 해당 대화에서 사용 가능한 연결 도구를 통해 수행합니다. 일반 ChatGPT 대화에서 이미지가 생성될 때마다 시작되는 백그라운드 연동은 제공되지 않습니다.

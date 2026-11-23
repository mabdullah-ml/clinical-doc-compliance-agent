# 治験・規制文書 整合性チェック＆CTD自動ドラフト生成エージェント

> 🌐 **[English Documentation (README.md)](./README.md)**

製薬・ヘルスケア・リーガル領域の規制文書（**治験実施計画書 Protocol / 治験薬概要書 IB / CTD Module 2.5**）を対象に、**文書間の数値・安全性矛盾（投与量・目標症例数・重篤な有害事象SAE件数等）を自動検知し、根拠引用付きの統合CTDドラフトを生成する**フルスタック生成AIアプリケーション（FastAPI + Pydantic v2 + Next.js 15 TypeScript + Docker）です。

※同梱サンプルデータ（`AMX-402-P2`）はすべて架空の合成データです。

## クイックスタート

```bash
docker compose up --build
```

- **コンプライアンス審査UI:** `http://localhost:3000`
- **FastAPI Swagger UI:** `http://localhost:8000/docs`

## 作成者

**あぶどら・まもん（工学博士 / PMP）**  
[GitHub](https://github.com/mabdullah-ml) · [LinkedIn](https://www.linkedin.com/in/mamunabdullah01)

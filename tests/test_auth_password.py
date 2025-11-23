"""パスワードハッシュ化と検証のテスト"""
from app.core.security import get_password_hash, verify_password


def test_password_hash_and_verify():
    """パスワードのハッシュ化と検証をテスト"""
    # テスト用パスワード
    plain_password = "TestPass123!"
    
    # パスワードをハッシュ化
    hashed = get_password_hash(plain_password)
    print(f"ハッシュ化されたパスワード: {hashed[:50]}...")
    
    # 正しいパスワードで検証
    assert verify_password(plain_password, hashed), "正しいパスワードで検証が失敗"
    print("✓ 正しいパスワードで検証成功")
    
    # 間違ったパスワードで検証
    wrong_password = "WrongPass123!"
    assert not verify_password(wrong_password, hashed), "間違ったパスワードで検証が成功してしまった"
    print("✓ 間違ったパスワードで検証失敗（期待通り）")
    
    # 同じパスワードを再度ハッシュ化しても異なるハッシュになることを確認
    hashed2 = get_password_hash(plain_password)
    assert hashed != hashed2, "同じパスワードでも異なるハッシュが生成されるべき"
    print("✓ 同じパスワードでも異なるハッシュが生成されることを確認")
    
    # 両方のハッシュで元のパスワードが検証できることを確認
    assert verify_password(plain_password, hashed2), "2回目のハッシュで検証が失敗"
    print("✓ 2回目のハッシュでも検証成功")
    
    print("\nすべてのテストが成功しました！")


if __name__ == "__main__":
    test_password_hash_and_verify()


#!/bin/bash

# 学院1.0 项目上传到GitHub

echo "=== 1. 初始化Git仓库 ==="
git init

echo ""
echo "=== 2. 添加.gitignore文件 ==="
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
*.egg-info/
dist/
build/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
package-lock.json
yarn.lock

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Django
*.log
local_settings.py
db.sqlite3
media/
staticfiles/

# Environment
.env
.env.local
*.local

# Test
.coverage
htmlcov/
.pytest_cache/
EOF

echo ""
echo "=== 3. 添加所有文件 ==="
git add .

echo ""
echo "=== 4. 首次提交 ==="
git commit -m "Initial commit: 学院1.0 OA系统"

echo ""
echo "=== 5. 重命名分支为main ==="
git branch -M main

echo ""
echo "=== 6. 添加远程仓库 ==="
# 请将下面链接替换为您创建的GitHub仓库地址
# 如果您还没有创建仓库，请先在GitHub上创建名为 "1.00" 的空仓库
git remote add origin https://github.com/mbin/1.00.git

echo ""
echo "=== 7. 推送到GitHub ==="
git push -u origin main

echo ""
echo "=== 完成! ==="
echo "如果推送失败，可能需要先在GitHub上创建名为 '1.00' 的空仓库"

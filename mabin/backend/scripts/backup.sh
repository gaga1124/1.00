#!/bin/bash
# 数据库备份脚本

BACKUP_DIR="/backup/college_oa"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="college_oa"
DB_USER="root"
DB_PASSWORD="your_password"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u$DB_USER -p$DB_PASSWORD $DB_NAME > $BACKUP_DIR/db_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/db_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +7 -delete

echo "备份完成: $BACKUP_DIR/db_$DATE.sql.gz"

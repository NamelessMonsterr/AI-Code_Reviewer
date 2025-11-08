#!/bin/bash
set -e

BACKUP_DIR="backups/$(date +%Y%m%d-%H%M%S)"

echo "💾 Creating backup..."
echo "Backup directory: $BACKUP_DIR"
echo ""

mkdir -p "$BACKUP_DIR"

# Backup database
echo "Backing up database..."
docker-compose exec -T postgres pg_dump -U postgres review_bot > "$BACKUP_DIR/database.sql"

# Backup data directory
echo "Backing up data..."
tar -czf "$BACKUP_DIR/data.tar.gz" data/

# Backup config
echo "Backing up config..."
tar -czf "$BACKUP_DIR/config.tar.gz" config/

# Backup .env (encrypted)
echo "Backing up .env..."
cp .env "$BACKUP_DIR/.env"

echo ""
echo "✅ Backup complete!"
echo "Location: $BACKUP_DIR"
echo ""
echo "To restore:"
echo "  ./scripts/restore.sh $BACKUP_DIR"


# ============================================
# FILE: scripts/restore.sh
# ============================================
#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Usage: ./scripts/restore.sh <backup_directory>"
    exit 1
fi

BACKUP_DIR=$1

if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ Backup directory not found: $BACKUP_DIR"
    exit 1
fi

echo "♻️  Restoring from backup: $BACKUP_DIR"
echo ""
read -p "This will overwrite current data. Continue? (yes/no) " -r
echo
if [[ ! $REPLY = "yes" ]]; then
    echo "Restore cancelled"
    exit 1
fi

# Restore database
if [ -f "$BACKUP_DIR/database.sql" ]; then
    echo "Restoring database..."
    docker-compose exec -T postgres psql -U postgres review_bot < "$BACKUP_DIR/database.sql"
fi

# Restore data
if [ -f "$BACKUP_DIR/data.tar.gz" ]; then
    echo "Restoring data..."
    tar -xzf "$BACKUP_DIR/data.tar.gz"
fi

# Restore config
if [ -f "$BACKUP_DIR/config.tar.gz" ]; then
    echo "Restoring config..."
    tar -xzf "$BACKUP_DIR/config.tar.gz"
fi

echo ""
echo "✅ Restore complete!"
echo "Restart services: docker-compose restart"

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `secondtable1` (
    `id` BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT COMMENT '主键',
    `created_at` DATETIME(6) NOT NULL COMMENT '创建时间' DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL COMMENT '更新时间' DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `deleted_at` BIGINT COMMENT '删除时间',
    `a` VARCHAR(10) NOT NULL COMMENT 'a',
    `b` VARCHAR(10) NOT NULL COMMENT 'b',
    KEY `idx_secondtable_created_1b6e5f` (`created_at`),
    KEY `idx_secondtable_deleted_9a99e1` (`deleted_at`)
) CHARACTER SET utf8mb4 COMMENT='Second Table 1';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """

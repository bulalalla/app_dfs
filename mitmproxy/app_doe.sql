/*
 Navicat Premium Data Transfer

 Source Server         : localhost
 Source Server Type    : MySQL
 Source Server Version : 80032
 Source Host           : localhost:3306
 Source Schema         : app_doe

 Target Server Type    : MySQL
 Target Server Version : 80032
 File Encoding         : 65001

 Date: 29/09/2024 19:45:07
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for app_domain_dns
-- ----------------------------
DROP TABLE IF EXISTS `app_domain_dns`;
CREATE TABLE `app_domain_dns`  (
  `package_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'app的包名',
  `method` enum('MITM','eCapture','Analyze') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `protocol` enum('DNS','HTTPS','TLS_SNI') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'DNS' COMMENT '此条数据从何协议数据包提取',
  `qrcode` enum('0','1') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT '0' COMMENT '0表查询，1表响应',
  `question` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `response` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `domains` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '请求或响应涉及到的域名',
  `add_time` datetime NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '此数据加入的时间'
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for app_domain_https
-- ----------------------------
DROP TABLE IF EXISTS `app_domain_https`;
CREATE TABLE `app_domain_https`  (
  `package_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'app的包名',
  `method` enum('MITM','eCapture','Analyze') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `protocol` enum('DNS','HTTPS','TLS_SNI') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'HTTPS' COMMENT '此条数据从何协议数据包提取',
  `qrvalue` enum('RESPONSE','GET','POST','HEAD','PUT','DELETE','CONNECT''OPTIONS','TRACE') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'GET' COMMENT '响应/请求类型',
  `host` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `uri_path` varchar(8192) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `content_type` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `data` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT '请求或响应携带的数据，太长会被截断',
  `add_time` datetime NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '此数据加入的时间'
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for app_domain_tls_sni
-- ----------------------------
DROP TABLE IF EXISTS `app_domain_tls_sni`;
CREATE TABLE `app_domain_tls_sni`  (
  `package_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'app的包名',
  `method` enum('MITM','eCapture','Analyze') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL,
  `protocol` enum('DNS','HTTPS','TLS_SNI') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT 'TLS_SNI' COMMENT '此条数据从何协议数据包提取',
  `sni` varchar(1024) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NULL DEFAULT NULL COMMENT 'sni',
  `add_time` datetime NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '此数据加入的时间'
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for app_domains_copy1
-- ----------------------------
DROP TABLE IF EXISTS `app_domains_copy1`;
CREATE TABLE `app_domains_copy1`  (
  `packet_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '应用程序包名',
  `capture_method` enum('MITM','eCapture') CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL COMMENT '捕获方式，应该为 \'MITM\' 和 \'eCapture\' 中的一个',
  `protocol_type` enum('DNS','HTTPS','HTTP','TLS_Client_Hello') CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL COMMENT '协议类型，当前只考虑了 \'DNS\' 和 ‘HTTPS’',
  `domain` varchar(255) CHARACTER SET gbk COLLATE gbk_chinese_ci NOT NULL COMMENT '协议中的域名',
  `full_uri` text CHARACTER SET gbk COLLATE gbk_chinese_ci NULL,
  `date` datetime NOT NULL COMMENT '更新时间'
) ENGINE = InnoDB CHARACTER SET = gbk COLLATE = gbk_chinese_ci ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;

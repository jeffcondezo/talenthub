/*
 Navicat Premium Data Transfer

 Source Server         : local
 Source Server Type    : MySQL
 Source Server Version : 100427 (10.4.27-MariaDB)
 Source Host           : localhost:3306
 Source Schema         : talenthub

 Target Server Type    : MySQL
 Target Server Version : 100427 (10.4.27-MariaDB)
 File Encoding         : 65001

 Date: 24/09/2025 16:30:13
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for auth_group
-- ----------------------------
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_group
-- ----------------------------

-- ----------------------------
-- Table structure for auth_group_permissions
-- ----------------------------
DROP TABLE IF EXISTS `auth_group_permissions`;
CREATE TABLE `auth_group_permissions`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_group_permissions_group_id_permission_id_0cd325b0_uniq`(`group_id` ASC, `permission_id` ASC) USING BTREE,
  INDEX `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm`(`permission_id` ASC) USING BTREE,
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_group_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for auth_permission
-- ----------------------------
DROP TABLE IF EXISTS `auth_permission`;
CREATE TABLE `auth_permission`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_permission_content_type_id_codename_01ab375a_uniq`(`content_type_id` ASC, `codename` ASC) USING BTREE,
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 77 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_permission
-- ----------------------------
INSERT INTO `auth_permission` VALUES (1, 'Can add log entry', 1, 'add_logentry');
INSERT INTO `auth_permission` VALUES (2, 'Can change log entry', 1, 'change_logentry');
INSERT INTO `auth_permission` VALUES (3, 'Can delete log entry', 1, 'delete_logentry');
INSERT INTO `auth_permission` VALUES (4, 'Can view log entry', 1, 'view_logentry');
INSERT INTO `auth_permission` VALUES (5, 'Can add permission', 2, 'add_permission');
INSERT INTO `auth_permission` VALUES (6, 'Can change permission', 2, 'change_permission');
INSERT INTO `auth_permission` VALUES (7, 'Can delete permission', 2, 'delete_permission');
INSERT INTO `auth_permission` VALUES (8, 'Can view permission', 2, 'view_permission');
INSERT INTO `auth_permission` VALUES (9, 'Can add group', 3, 'add_group');
INSERT INTO `auth_permission` VALUES (10, 'Can change group', 3, 'change_group');
INSERT INTO `auth_permission` VALUES (11, 'Can delete group', 3, 'delete_group');
INSERT INTO `auth_permission` VALUES (12, 'Can view group', 3, 'view_group');
INSERT INTO `auth_permission` VALUES (13, 'Can add user', 4, 'add_user');
INSERT INTO `auth_permission` VALUES (14, 'Can change user', 4, 'change_user');
INSERT INTO `auth_permission` VALUES (15, 'Can delete user', 4, 'delete_user');
INSERT INTO `auth_permission` VALUES (16, 'Can view user', 4, 'view_user');
INSERT INTO `auth_permission` VALUES (17, 'Can add content type', 5, 'add_contenttype');
INSERT INTO `auth_permission` VALUES (18, 'Can change content type', 5, 'change_contenttype');
INSERT INTO `auth_permission` VALUES (19, 'Can delete content type', 5, 'delete_contenttype');
INSERT INTO `auth_permission` VALUES (20, 'Can view content type', 5, 'view_contenttype');
INSERT INTO `auth_permission` VALUES (21, 'Can add session', 6, 'add_session');
INSERT INTO `auth_permission` VALUES (22, 'Can change session', 6, 'change_session');
INSERT INTO `auth_permission` VALUES (23, 'Can delete session', 6, 'delete_session');
INSERT INTO `auth_permission` VALUES (24, 'Can view session', 6, 'view_session');
INSERT INTO `auth_permission` VALUES (25, 'Can add Área', 7, 'add_area');
INSERT INTO `auth_permission` VALUES (26, 'Can change Área', 7, 'change_area');
INSERT INTO `auth_permission` VALUES (27, 'Can delete Área', 7, 'delete_area');
INSERT INTO `auth_permission` VALUES (28, 'Can view Área', 7, 'view_area');
INSERT INTO `auth_permission` VALUES (29, 'Can add Cargo', 8, 'add_cargo');
INSERT INTO `auth_permission` VALUES (30, 'Can change Cargo', 8, 'change_cargo');
INSERT INTO `auth_permission` VALUES (31, 'Can delete Cargo', 8, 'delete_cargo');
INSERT INTO `auth_permission` VALUES (32, 'Can view Cargo', 8, 'view_cargo');
INSERT INTO `auth_permission` VALUES (33, 'Can add Convocatoria', 9, 'add_convocatoria');
INSERT INTO `auth_permission` VALUES (34, 'Can change Convocatoria', 9, 'change_convocatoria');
INSERT INTO `auth_permission` VALUES (35, 'Can delete Convocatoria', 9, 'delete_convocatoria');
INSERT INTO `auth_permission` VALUES (36, 'Can view Convocatoria', 9, 'view_convocatoria');
INSERT INTO `auth_permission` VALUES (37, 'Can add CV', 10, 'add_cv');
INSERT INTO `auth_permission` VALUES (38, 'Can change CV', 10, 'change_cv');
INSERT INTO `auth_permission` VALUES (39, 'Can delete CV', 10, 'delete_cv');
INSERT INTO `auth_permission` VALUES (40, 'Can view CV', 10, 'view_cv');
INSERT INTO `auth_permission` VALUES (41, 'Can add Departamento', 11, 'add_departamento');
INSERT INTO `auth_permission` VALUES (42, 'Can change Departamento', 11, 'change_departamento');
INSERT INTO `auth_permission` VALUES (43, 'Can delete Departamento', 11, 'delete_departamento');
INSERT INTO `auth_permission` VALUES (44, 'Can view Departamento', 11, 'view_departamento');
INSERT INTO `auth_permission` VALUES (45, 'Can add Distrito', 12, 'add_distrito');
INSERT INTO `auth_permission` VALUES (46, 'Can change Distrito', 12, 'change_distrito');
INSERT INTO `auth_permission` VALUES (47, 'Can delete Distrito', 12, 'delete_distrito');
INSERT INTO `auth_permission` VALUES (48, 'Can view Distrito', 12, 'view_distrito');
INSERT INTO `auth_permission` VALUES (49, 'Can add Provincia', 13, 'add_provincia');
INSERT INTO `auth_permission` VALUES (50, 'Can change Provincia', 13, 'change_provincia');
INSERT INTO `auth_permission` VALUES (51, 'Can delete Provincia', 13, 'delete_provincia');
INSERT INTO `auth_permission` VALUES (52, 'Can view Provincia', 13, 'view_provincia');
INSERT INTO `auth_permission` VALUES (53, 'Can add Persona', 14, 'add_persona');
INSERT INTO `auth_permission` VALUES (54, 'Can change Persona', 14, 'change_persona');
INSERT INTO `auth_permission` VALUES (55, 'Can delete Persona', 14, 'delete_persona');
INSERT INTO `auth_permission` VALUES (56, 'Can view Persona', 14, 'view_persona');
INSERT INTO `auth_permission` VALUES (57, 'Can add Formación Académica', 15, 'add_formacionacademica');
INSERT INTO `auth_permission` VALUES (58, 'Can change Formación Académica', 15, 'change_formacionacademica');
INSERT INTO `auth_permission` VALUES (59, 'Can delete Formación Académica', 15, 'delete_formacionacademica');
INSERT INTO `auth_permission` VALUES (60, 'Can view Formación Académica', 15, 'view_formacionacademica');
INSERT INTO `auth_permission` VALUES (61, 'Can add Experiencia Laboral', 16, 'add_experiencialaboral');
INSERT INTO `auth_permission` VALUES (62, 'Can change Experiencia Laboral', 16, 'change_experiencialaboral');
INSERT INTO `auth_permission` VALUES (63, 'Can delete Experiencia Laboral', 16, 'delete_experiencialaboral');
INSERT INTO `auth_permission` VALUES (64, 'Can view Experiencia Laboral', 16, 'view_experiencialaboral');
INSERT INTO `auth_permission` VALUES (65, 'Can add Curso de Especialización', 17, 'add_cursoespecializacion');
INSERT INTO `auth_permission` VALUES (66, 'Can change Curso de Especialización', 17, 'change_cursoespecializacion');
INSERT INTO `auth_permission` VALUES (67, 'Can delete Curso de Especialización', 17, 'delete_cursoespecializacion');
INSERT INTO `auth_permission` VALUES (68, 'Can view Curso de Especialización', 17, 'view_cursoespecializacion');
INSERT INTO `auth_permission` VALUES (69, 'Can add Colaborador', 18, 'add_colaborador');
INSERT INTO `auth_permission` VALUES (70, 'Can change Colaborador', 18, 'change_colaborador');
INSERT INTO `auth_permission` VALUES (71, 'Can delete Colaborador', 18, 'delete_colaborador');
INSERT INTO `auth_permission` VALUES (72, 'Can view Colaborador', 18, 'view_colaborador');
INSERT INTO `auth_permission` VALUES (73, 'Can add Postulación', 19, 'add_postulacion');
INSERT INTO `auth_permission` VALUES (74, 'Can change Postulación', 19, 'change_postulacion');
INSERT INTO `auth_permission` VALUES (75, 'Can delete Postulación', 19, 'delete_postulacion');
INSERT INTO `auth_permission` VALUES (76, 'Can view Postulación', 19, 'view_postulacion');

-- ----------------------------
-- Table structure for auth_user
-- ----------------------------
DROP TABLE IF EXISTS `auth_user`;
CREATE TABLE `auth_user`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `last_login` datetime(6) NULL DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `first_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `last_name` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_user
-- ----------------------------

-- ----------------------------
-- Table structure for auth_user_groups
-- ----------------------------
DROP TABLE IF EXISTS `auth_user_groups`;
CREATE TABLE `auth_user_groups`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_user_groups_user_id_group_id_94350c0c_uniq`(`user_id` ASC, `group_id` ASC) USING BTREE,
  INDEX `auth_user_groups_group_id_97559544_fk_auth_group_id`(`group_id` ASC) USING BTREE,
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_user_groups
-- ----------------------------

-- ----------------------------
-- Table structure for auth_user_user_permissions
-- ----------------------------
DROP TABLE IF EXISTS `auth_user_user_permissions`;
CREATE TABLE `auth_user_user_permissions`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq`(`user_id` ASC, `permission_id` ASC) USING BTREE,
  INDEX `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm`(`permission_id` ASC) USING BTREE,
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of auth_user_user_permissions
-- ----------------------------

-- ----------------------------
-- Table structure for django_admin_log
-- ----------------------------
DROP TABLE IF EXISTS `django_admin_log`;
CREATE TABLE `django_admin_log`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `object_repr` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `action_flag` smallint UNSIGNED NOT NULL,
  `change_message` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `content_type_id` int NULL DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `django_admin_log_content_type_id_c4bce8eb_fk_django_co`(`content_type_id` ASC) USING BTREE,
  INDEX `django_admin_log_user_id_c564eba6_fk_auth_user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of django_admin_log
-- ----------------------------

-- ----------------------------
-- Table structure for django_content_type
-- ----------------------------
DROP TABLE IF EXISTS `django_content_type`;
CREATE TABLE `django_content_type`  (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `model` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `django_content_type_app_label_model_76bd3d3b_uniq`(`app_label` ASC, `model` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 20 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of django_content_type
-- ----------------------------
INSERT INTO `django_content_type` VALUES (1, 'admin', 'logentry');
INSERT INTO `django_content_type` VALUES (3, 'auth', 'group');
INSERT INTO `django_content_type` VALUES (2, 'auth', 'permission');
INSERT INTO `django_content_type` VALUES (4, 'auth', 'user');
INSERT INTO `django_content_type` VALUES (5, 'contenttypes', 'contenttype');
INSERT INTO `django_content_type` VALUES (7, 'master', 'area');
INSERT INTO `django_content_type` VALUES (8, 'master', 'cargo');
INSERT INTO `django_content_type` VALUES (18, 'master', 'colaborador');
INSERT INTO `django_content_type` VALUES (9, 'master', 'convocatoria');
INSERT INTO `django_content_type` VALUES (17, 'master', 'cursoespecializacion');
INSERT INTO `django_content_type` VALUES (10, 'master', 'cv');
INSERT INTO `django_content_type` VALUES (11, 'master', 'departamento');
INSERT INTO `django_content_type` VALUES (12, 'master', 'distrito');
INSERT INTO `django_content_type` VALUES (16, 'master', 'experiencialaboral');
INSERT INTO `django_content_type` VALUES (15, 'master', 'formacionacademica');
INSERT INTO `django_content_type` VALUES (14, 'master', 'persona');
INSERT INTO `django_content_type` VALUES (19, 'master', 'postulacion');
INSERT INTO `django_content_type` VALUES (13, 'master', 'provincia');
INSERT INTO `django_content_type` VALUES (6, 'sessions', 'session');

-- ----------------------------
-- Table structure for django_migrations
-- ----------------------------
DROP TABLE IF EXISTS `django_migrations`;
CREATE TABLE `django_migrations`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 23 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of django_migrations
-- ----------------------------
INSERT INTO `django_migrations` VALUES (1, 'contenttypes', '0001_initial', '2025-09-17 18:31:05.369042');
INSERT INTO `django_migrations` VALUES (2, 'auth', '0001_initial', '2025-09-17 18:31:05.651140');
INSERT INTO `django_migrations` VALUES (3, 'admin', '0001_initial', '2025-09-17 18:31:05.723839');
INSERT INTO `django_migrations` VALUES (4, 'admin', '0002_logentry_remove_auto_add', '2025-09-17 18:31:05.729648');
INSERT INTO `django_migrations` VALUES (5, 'admin', '0003_logentry_add_action_flag_choices', '2025-09-17 18:31:05.736299');
INSERT INTO `django_migrations` VALUES (6, 'contenttypes', '0002_remove_content_type_name', '2025-09-17 18:31:05.769476');
INSERT INTO `django_migrations` VALUES (7, 'auth', '0002_alter_permission_name_max_length', '2025-09-17 18:31:05.804161');
INSERT INTO `django_migrations` VALUES (8, 'auth', '0003_alter_user_email_max_length', '2025-09-17 18:31:05.813305');
INSERT INTO `django_migrations` VALUES (9, 'auth', '0004_alter_user_username_opts', '2025-09-17 18:31:05.820395');
INSERT INTO `django_migrations` VALUES (10, 'auth', '0005_alter_user_last_login_null', '2025-09-17 18:31:05.845235');
INSERT INTO `django_migrations` VALUES (11, 'auth', '0006_require_contenttypes_0002', '2025-09-17 18:31:05.847257');
INSERT INTO `django_migrations` VALUES (12, 'auth', '0007_alter_validators_add_error_messages', '2025-09-17 18:31:05.853307');
INSERT INTO `django_migrations` VALUES (13, 'auth', '0008_alter_user_username_max_length', '2025-09-17 18:31:05.862987');
INSERT INTO `django_migrations` VALUES (14, 'auth', '0009_alter_user_last_name_max_length', '2025-09-17 18:31:05.873665');
INSERT INTO `django_migrations` VALUES (15, 'auth', '0010_alter_group_name_max_length', '2025-09-17 18:31:05.883788');
INSERT INTO `django_migrations` VALUES (16, 'auth', '0011_update_proxy_permissions', '2025-09-17 18:31:05.889867');
INSERT INTO `django_migrations` VALUES (17, 'auth', '0012_alter_user_first_name_max_length', '2025-09-17 18:31:05.899994');
INSERT INTO `django_migrations` VALUES (18, 'master', '0001_initial', '2025-09-17 18:31:06.826459');
INSERT INTO `django_migrations` VALUES (19, 'sessions', '0001_initial', '2025-09-17 18:31:06.845561');
INSERT INTO `django_migrations` VALUES (20, 'master', '0002_convocatoria_nombre_empresa_externa', '2025-09-24 16:07:15.370519');
INSERT INTO `django_migrations` VALUES (21, 'master', '0003_auto_20250924_1106', '2025-09-24 16:07:15.372982');
INSERT INTO `django_migrations` VALUES (22, 'master', '0004_alter_experiencialaboral_motivo_salida', '2025-09-24 18:18:40.670696');

-- ----------------------------
-- Table structure for django_session
-- ----------------------------
DROP TABLE IF EXISTS `django_session`;
CREATE TABLE `django_session`  (
  `session_key` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `session_data` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`) USING BTREE,
  INDEX `django_session_expire_date_a5c62663`(`expire_date` ASC) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of django_session
-- ----------------------------
INSERT INTO `django_session` VALUES ('kgb8lmcfp1ct4k32wk68zl6k1h9pugrs', 'e30:1v1UAO:q1iCSIZlTdx8_pckJYQtg-JoVfI71sabhNA8SvijSkw', '2025-09-25 18:24:36.918701');
INSERT INTO `django_session` VALUES ('t8auc2fi8xuwe4x03vrmee6a0vomfb8d', 'e30:1uzN9x:uBqhra5AhauyoEkuP9-OPoHxb0mIhkPPeY0pX1NZK-o', '2025-09-19 22:31:25.446191');

-- ----------------------------
-- Table structure for master_area
-- ----------------------------
DROP TABLE IF EXISTS `master_area`;
CREATE TABLE `master_area`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `descripcion` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `activo` tinyint(1) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `nombre`(`nombre` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_area
-- ----------------------------
INSERT INTO `master_area` VALUES (1, 'Tecnología', 'Área de tecnología e innovación', 1, '2025-09-17 19:03:22.491833');
INSERT INTO `master_area` VALUES (2, 'Recursos Humanos', 'Área de recursos humanos y gestión del talento', 1, '2025-09-17 19:03:22.496951');
INSERT INTO `master_area` VALUES (3, 'Finanzas', 'Área de finanzas y contabilidad', 1, '2025-09-17 19:03:22.501934');
INSERT INTO `master_area` VALUES (4, 'Marketing', 'Área de marketing y comunicaciones', 1, '2025-09-17 19:03:22.503943');

-- ----------------------------
-- Table structure for master_cargo
-- ----------------------------
DROP TABLE IF EXISTS `master_cargo`;
CREATE TABLE `master_cargo`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `descripcion` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `nivel` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `salario_minimo` decimal(10, 2) NULL DEFAULT NULL,
  `salario_maximo` decimal(10, 2) NULL DEFAULT NULL,
  `activo` tinyint(1) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `area_id` bigint NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `master_cargo_area_id_nombre_645ea1ff_uniq`(`area_id` ASC, `nombre` ASC) USING BTREE,
  CONSTRAINT `master_cargo_area_id_a18fb4fb_fk_master_area_id` FOREIGN KEY (`area_id`) REFERENCES `master_area` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_cargo
-- ----------------------------
INSERT INTO `master_cargo` VALUES (1, 'Desarrollador Frontend', 'Desarrollador especializado en tecnologías frontend', 'JUNIOR', NULL, NULL, 1, '2025-09-17 19:03:22.508050', 1);
INSERT INTO `master_cargo` VALUES (2, 'Analista de Sistemas', 'Analista especializado en análisis y diseño de sistemas', 'SENIOR', NULL, NULL, 1, '2025-09-17 19:03:22.511076', 1);
INSERT INTO `master_cargo` VALUES (3, 'Diseñador UX/UI', 'Diseñador especializado en experiencia de usuario e interfaz', 'MID', NULL, NULL, 1, '2025-09-17 19:03:22.514241', 4);
INSERT INTO `master_cargo` VALUES (4, 'Especialista en RRHH', 'Especialista en recursos humanos y gestión del talento', 'MID', NULL, NULL, 1, '2025-09-17 19:03:22.517366', 2);
INSERT INTO `master_cargo` VALUES (5, 'Contador', 'Contador especializado en contabilidad y finanzas', 'SENIOR', NULL, NULL, 1, '2025-09-17 19:03:22.519056', 3);

-- ----------------------------
-- Table structure for master_colaborador
-- ----------------------------
DROP TABLE IF EXISTS `master_colaborador`;
CREATE TABLE `master_colaborador`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_ingreso` date NOT NULL,
  `fecha_salida` date NULL DEFAULT NULL,
  `estado_laboral` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `tipo_contrato` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `salario` decimal(10, 2) NULL DEFAULT NULL,
  `numero_empleado` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `fecha_ultima_evaluacion` date NULL DEFAULT NULL,
  `notas_laborales` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `cargo_id` bigint NOT NULL,
  `persona_id` bigint NULL DEFAULT NULL,
  `supervisor_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `numero_empleado`(`numero_empleado` ASC) USING BTREE,
  UNIQUE INDEX `persona_id`(`persona_id` ASC) USING BTREE,
  INDEX `master_cola_estado__b6b22d_idx`(`estado_laboral` ASC) USING BTREE,
  INDEX `master_cola_fecha_i_f46a61_idx`(`fecha_ingreso` ASC) USING BTREE,
  INDEX `master_cola_cargo_i_d5902a_idx`(`cargo_id` ASC) USING BTREE,
  INDEX `master_cola_numero__d76d3f_idx`(`numero_empleado` ASC) USING BTREE,
  INDEX `master_colaborador_supervisor_id_f21527b5_fk_master_co`(`supervisor_id` ASC) USING BTREE,
  CONSTRAINT `master_colaborador_cargo_id_44540304_fk_master_cargo_id` FOREIGN KEY (`cargo_id`) REFERENCES `master_cargo` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `master_colaborador_persona_id_ff00e760_fk_master_persona_id` FOREIGN KEY (`persona_id`) REFERENCES `master_persona` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `master_colaborador_supervisor_id_f21527b5_fk_master_co` FOREIGN KEY (`supervisor_id`) REFERENCES `master_colaborador` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_colaborador
-- ----------------------------

-- ----------------------------
-- Table structure for master_convocatoria
-- ----------------------------
DROP TABLE IF EXISTS `master_convocatoria`;
CREATE TABLE `master_convocatoria`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `titulo` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `descripcion` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `fecha_apertura` datetime(6) NOT NULL,
  `fecha_cierre` datetime(6) NOT NULL,
  `fecha_inicio_trabajo` date NULL DEFAULT NULL,
  `estado` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `tipo` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `requisitos_minimos` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `requisitos_deseables` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `experiencia_minima` int UNSIGNED NOT NULL,
  `numero_vacantes` int UNSIGNED NOT NULL,
  `salario_ofrecido` decimal(10, 2) NULL DEFAULT NULL,
  `modalidad_trabajo` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `ubicacion` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `responsable_rrhh` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `activo` tinyint(1) NOT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `cargo_id` bigint NOT NULL,
  `nombre_empresa_externa` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `master_conv_estado_3db3c3_idx`(`estado` ASC) USING BTREE,
  INDEX `master_conv_cargo_i_cca6e2_idx`(`cargo_id` ASC) USING BTREE,
  INDEX `master_conv_fecha_a_cef31f_idx`(`fecha_apertura` ASC, `fecha_cierre` ASC) USING BTREE,
  CONSTRAINT `master_convocatoria_cargo_id_dd03ae62_fk_master_cargo_id` FOREIGN KEY (`cargo_id`) REFERENCES `master_cargo` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_convocatoria
-- ----------------------------
INSERT INTO `master_convocatoria` VALUES (1, 'Desarrollador Frontend - Lima', '\n            Buscamos un desarrollador frontend con experiencia en React, Vue.js o Angular.\n            Responsable de desarrollar interfaces de usuario atractivas y funcionales.\n            \n            Responsabilidades:\n            - Desarrollar componentes reutilizables\n            - Optimizar aplicaciones para máxima velocidad y escalabilidad\n            - Colaborar con el equipo de diseño y backend\n            - Mantener y mejorar código existente\n            ', '2025-09-17 19:04:15.630897', '2025-10-17 19:04:15.630897', '2025-11-01', 'PUBLICADA', 'EXTERNA', '\n            - 2+ años de experiencia en desarrollo frontend\n            - Conocimiento sólido en HTML5, CSS3, JavaScript\n            - Experiencia con al menos un framework (React, Vue.js, Angular)\n            - Conocimiento de Git y control de versiones\n            - Inglés intermedio\n            ', '\n            - Experiencia con TypeScript\n            - Conocimiento de herramientas de build (Webpack, Vite)\n            - Experiencia con testing (Jest, Cypress)\n            - Conocimiento de metodologías ágiles\n            ', 0, 1, 4500.00, 'PRESENCIAL', 'Lima, Perú', NULL, 1, '2025-09-17 19:04:15.633492', '2025-09-17 19:04:15.633492', 1, NULL);
INSERT INTO `master_convocatoria` VALUES (2, 'Analista de Sistemas - Arequipa', '\n            Buscamos un analista de sistemas senior para liderar proyectos de desarrollo\n            y análisis de requerimientos.\n            \n            Responsabilidades:\n            - Analizar y documentar requerimientos del negocio\n            - Diseñar soluciones técnicas\n            - Coordinar con equipos de desarrollo\n            - Realizar pruebas de sistemas\n            - Capacitar usuarios finales\n            ', '2025-09-17 19:04:15.630897', '2025-10-17 19:04:15.630897', '2025-11-01', 'PUBLICADA', 'EXTERNA', '\n            - 5+ años de experiencia en análisis de sistemas\n            - Conocimiento en metodologías de desarrollo (UML, BPMN)\n            - Experiencia con bases de datos (SQL Server, Oracle, MySQL)\n            - Conocimiento de lenguajes de programación (Java, C#, Python)\n            - Inglés avanzado\n            ', '\n            - Certificaciones en análisis de sistemas\n            - Experiencia con herramientas de modelado (Visio, Enterprise Architect)\n            - Conocimiento de metodologías ágiles (Scrum, Kanban)\n            - Experiencia en gestión de proyectos\n            ', 0, 1, 5750.00, 'PRESENCIAL', 'Arequipa, Perú', NULL, 1, '2025-09-17 19:04:15.635500', '2025-09-17 19:04:15.635500', 2, NULL);
INSERT INTO `master_convocatoria` VALUES (3, 'Diseñador UX/UI - Cusco', '\n            Buscamos un diseñador UX/UI creativo y orientado al usuario para diseñar\n            experiencias digitales excepcionales.\n            \n            Responsabilidades:\n            - Investigar y analizar necesidades de usuarios\n            - Crear wireframes, prototipos y mockups\n            - Diseñar interfaces intuitivas y atractivas\n            - Colaborar con desarrolladores frontend\n            - Realizar testing de usabilidad\n            ', '2025-09-17 19:04:15.630897', '2025-10-17 19:04:15.630897', '2025-11-01', 'PUBLICADA', 'EXTERNA', '\n            - 3+ años de experiencia en diseño UX/UI\n            - Dominio de herramientas de diseño (Figma, Adobe XD, Sketch)\n            - Conocimiento de principios de diseño y usabilidad\n            - Experiencia con metodologías de investigación de usuarios\n            - Portfolio demostrable\n            ', '\n            - Conocimiento de HTML/CSS básico\n            - Experiencia con herramientas de prototipado (InVision, Principle)\n            - Conocimiento de accesibilidad web\n            - Experiencia en diseño responsive\n            - Inglés intermedio\n            ', 0, 1, 4000.00, 'REMOTO', 'Cusco, Perú', NULL, 1, '2025-09-17 19:04:15.640639', '2025-09-17 19:04:15.640639', 3, NULL);
INSERT INTO `master_convocatoria` VALUES (4, 'Especialista en RRHH - Lima', '\n            Buscamos un especialista en recursos humanos para gestionar procesos\n            de selección, capacitación y desarrollo del talento.\n            \n            Responsabilidades:\n            - Gestionar procesos de reclutamiento y selección\n            - Coordinar programas de capacitación\n            - Administrar políticas de RRHH\n            - Realizar evaluaciones de desempeño\n            - Mantener relaciones laborales\n            ', '2025-09-17 19:04:15.630897', '2025-10-17 19:04:15.630897', '2025-11-01', 'PUBLICADA', 'EXTERNA', '\n            - 3+ años de experiencia en RRHH\n            - Conocimiento en legislación laboral\n            - Experiencia en procesos de selección\n            - Conocimiento de herramientas de RRHH\n            - Excelente comunicación interpersonal\n            ', '\n            - Certificación en RRHH\n            - Experiencia con sistemas de gestión de talento\n            - Conocimiento de psicología organizacional\n            - Experiencia en capacitación y desarrollo\n            - Inglés intermedio\n            ', 0, 1, 3500.00, 'PRESENCIAL', 'Lima, Perú', NULL, 1, '2025-09-17 19:04:15.643338', '2025-09-17 19:04:15.643338', 4, NULL);
INSERT INTO `master_convocatoria` VALUES (5, 'Contador Senior - Arequipa', 'Buscamos un contador senior para liderar procesos contables y financieros\r\n            de la organización.\r\n            \r\n            Responsabilidades:\r\n            - Liderar procesos contables y financieros\r\n            - Preparar estados financieros\r\n            - Gestionar auditorías\r\n            - Supervisar equipo contable\r\n            - Cumplir normativas fiscales', '2025-09-17 19:04:15.000000', '2025-10-17 19:04:15.000000', '2025-11-01', 'PUBLICADA', 'EXTERNA', '- 5+ años de experiencia en contabilidad\r\n            - Título profesional en Contabilidad\r\n            - Conocimiento de NIIF y NIC\r\n            - Experiencia con software contable\r\n            - Conocimiento de normativas fiscales', '- Certificación CPA o similar\r\n            - Experiencia en auditoría\r\n            - Conocimiento de sistemas ERP\r\n            - Experiencia en gestión de equipos\r\n            - Inglés intermedio', 0, 3, 5000.00, 'PRESENCIAL', 'Arequipa, Perú', NULL, 1, '2025-09-17 19:04:15.646395', '2025-09-24 16:30:54.318515', 5, NULL);
INSERT INTO `master_convocatoria` VALUES (6, 'Convocatoria Prueba', 'Desc', '2025-09-18 19:04:15.000000', '2025-09-19 19:04:15.000000', '2025-09-25', 'PUBLICADA', 'EXTERNA', 'qwe', '123', 2, 1, 500.00, 'PRESENCIAL', 'Arequipa, Perú', 'María González', 1, '2025-09-24 16:38:45.872499', '2025-09-24 16:47:18.559424', 3, 'Exte');
INSERT INTO `master_convocatoria` VALUES (7, 'CONVOCATORIA TEST', 'REST', '2025-09-24 11:52:00.000000', '2025-09-26 11:52:00.000000', '2025-09-27', 'EN_PROCESO', 'INTERNA', '- 5+ años de experiencia en contabilidad\r\n            - Título profesional en Contabilidad\r\n            - Conocimiento de NIIF y NIC\r\n            - Experiencia con software contable\r\n            - Conocimiento de normativas fiscales', '- Certificación CPA o similar\r\n            - Experiencia en auditoría\r\n            - Conocimiento de sistemas ERP\r\n            - Experiencia en gestión de equipos\r\n            - Inglés intermedio', 4, 4, 5000.00, 'PRESENCIAL', 'Arequipa, Perú', 'María González', 1, '2025-09-24 16:53:02.721774', '2025-09-24 16:53:02.721774', 4, NULL);

-- ----------------------------
-- Table structure for master_cursoespecializacion
-- ----------------------------
DROP TABLE IF EXISTS `master_cursoespecializacion`;
CREATE TABLE `master_cursoespecializacion`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tipo_estudio` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `descripcion` varchar(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `institucion` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `pais` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ciudad` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `horas_lectivas` int UNSIGNED NULL DEFAULT NULL,
  `nivel` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `certificado` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `observaciones` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `cv_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `master_curs_cv_id_30dd2c_idx`(`cv_id` ASC) USING BTREE,
  INDEX `master_curs_tipo_es_55b82b_idx`(`tipo_estudio` ASC) USING BTREE,
  CONSTRAINT `master_cursoespecializacion_cv_id_99987ba8_fk_master_cv_id` FOREIGN KEY (`cv_id`) REFERENCES `master_cv` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_cursoespecializacion
-- ----------------------------
INSERT INTO `master_cursoespecializacion` VALUES (1, 'CURSO', 'Curso de prueba', 'Universidad del Pacífico', 'Perú', 'Lima', '2025-09-10', '2025-09-26', 40, 'BASICO', '', 'Ninguna', '2025-09-18 03:33:19.096659', '2025-09-18 03:33:25.836064', 1);
INSERT INTO `master_cursoespecializacion` VALUES (2, 'CERTIFICACION', 'Certificacion', 'Universidad del Pacífico', 'Perú', 'Lima', '2025-09-10', '2025-09-17', 30, 'BASICO', '', 'Ninguna', '2025-09-18 03:34:19.650487', '2025-09-18 03:34:19.650487', 1);
INSERT INTO `master_cursoespecializacion` VALUES (3, 'CURSO', 'CURSO', 'Universidad del Pacífico', 'Perú', 'Lima', '2025-09-19', '2025-09-25', 22, 'BASICO', 'certificados/2509200006_202509200956533_BIOQ.pdf', 'n', '2025-09-24 18:09:23.704207', '2025-09-24 18:17:12.807177', 2);
INSERT INTO `master_cursoespecializacion` VALUES (4, 'CURSO', 'CURSO', 'Universidad del Pacífico', 'Perú', 'Lima', '2025-09-19', '2025-09-25', 22, 'INTERMEDIO', 'certificados/2509200006_2025092011135118_IMN.pdf', 'qwe', '2025-09-24 18:24:12.109792', '2025-09-24 18:24:12.111802', 2);

-- ----------------------------
-- Table structure for master_cv
-- ----------------------------
DROP TABLE IF EXISTS `master_cv`;
CREATE TABLE `master_cv`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `resumen_profesional` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `objetivo_profesional` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `telefono_profesional` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `email_profesional` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `linkedin` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `portfolio` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `cv_archivo` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `foto_perfil` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `persona_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `persona_id`(`persona_id` ASC) USING BTREE,
  INDEX `master_cv_persona_90c3f6_idx`(`persona_id` ASC) USING BTREE,
  INDEX `master_cv_fecha_a_a9d529_idx`(`fecha_actualizacion` ASC) USING BTREE,
  CONSTRAINT `master_cv_persona_id_6cf639dd_fk_master_persona_id` FOREIGN KEY (`persona_id`) REFERENCES `master_persona` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_cv
-- ----------------------------
INSERT INTO `master_cv` VALUES (1, NULL, NULL, NULL, NULL, NULL, NULL, '', '', '2025-09-18 03:28:57.697314', '2025-09-18 03:28:57.697314', 1);
INSERT INTO `master_cv` VALUES (2, '', '', NULL, NULL, NULL, NULL, '', '', '2025-09-24 17:26:29.867434', '2025-09-24 17:26:29.867434', 4);

-- ----------------------------
-- Table structure for master_departamento
-- ----------------------------
DROP TABLE IF EXISTS `master_departamento`;
CREATE TABLE `master_departamento`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `codigo` varchar(2) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `nombre`(`nombre` ASC) USING BTREE,
  UNIQUE INDEX `codigo`(`codigo` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 26 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_departamento
-- ----------------------------
INSERT INTO `master_departamento` VALUES (1, 'Amazonas', '01');
INSERT INTO `master_departamento` VALUES (2, 'Áncash', '02');
INSERT INTO `master_departamento` VALUES (3, 'Apurímac', '03');
INSERT INTO `master_departamento` VALUES (4, 'Arequipa', '04');
INSERT INTO `master_departamento` VALUES (5, 'Ayacucho', '05');
INSERT INTO `master_departamento` VALUES (6, 'Cajamarca', '06');
INSERT INTO `master_departamento` VALUES (7, 'Callao', '07');
INSERT INTO `master_departamento` VALUES (8, 'Cusco', '08');
INSERT INTO `master_departamento` VALUES (9, 'Huancavelica', '09');
INSERT INTO `master_departamento` VALUES (10, 'Huánuco', '10');
INSERT INTO `master_departamento` VALUES (11, 'Ica', '11');
INSERT INTO `master_departamento` VALUES (12, 'Junín', '12');
INSERT INTO `master_departamento` VALUES (13, 'La Libertad', '13');
INSERT INTO `master_departamento` VALUES (14, 'Lambayeque', '14');
INSERT INTO `master_departamento` VALUES (15, 'Lima', '15');
INSERT INTO `master_departamento` VALUES (16, 'Loreto', '16');
INSERT INTO `master_departamento` VALUES (17, 'Madre de Dios', '17');
INSERT INTO `master_departamento` VALUES (18, 'Moquegua', '18');
INSERT INTO `master_departamento` VALUES (19, 'Pasco', '19');
INSERT INTO `master_departamento` VALUES (20, 'Piura', '20');
INSERT INTO `master_departamento` VALUES (21, 'Puno', '21');
INSERT INTO `master_departamento` VALUES (22, 'San Martín', '22');
INSERT INTO `master_departamento` VALUES (23, 'Tacna', '23');
INSERT INTO `master_departamento` VALUES (24, 'Tumbes', '24');
INSERT INTO `master_departamento` VALUES (25, 'Ucayali', '25');

-- ----------------------------
-- Table structure for master_distrito
-- ----------------------------
DROP TABLE IF EXISTS `master_distrito`;
CREATE TABLE `master_distrito`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `codigo` varchar(6) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `provincia_id` bigint NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `master_distrito_codigo_provincia_id_cd2042c4_uniq`(`codigo` ASC, `provincia_id` ASC) USING BTREE,
  INDEX `master_distrito_provincia_id_0996864c_fk_master_provincia_id`(`provincia_id` ASC) USING BTREE,
  CONSTRAINT `master_distrito_provincia_id_0996864c_fk_master_provincia_id` FOREIGN KEY (`provincia_id`) REFERENCES `master_provincia` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 107 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_distrito
-- ----------------------------
INSERT INTO `master_distrito` VALUES (1, 'Lima', '150101', 1);
INSERT INTO `master_distrito` VALUES (2, 'Ancón', '150102', 1);
INSERT INTO `master_distrito` VALUES (3, 'Ate', '150103', 1);
INSERT INTO `master_distrito` VALUES (4, 'Barranco', '150104', 1);
INSERT INTO `master_distrito` VALUES (5, 'Breña', '150105', 1);
INSERT INTO `master_distrito` VALUES (6, 'Carabayllo', '150106', 1);
INSERT INTO `master_distrito` VALUES (7, 'Chaclacayo', '150107', 1);
INSERT INTO `master_distrito` VALUES (8, 'Chorrillos', '150108', 1);
INSERT INTO `master_distrito` VALUES (9, 'Cieneguilla', '150109', 1);
INSERT INTO `master_distrito` VALUES (10, 'Comas', '150110', 1);
INSERT INTO `master_distrito` VALUES (11, 'El Agustino', '150111', 1);
INSERT INTO `master_distrito` VALUES (12, 'Independencia', '150112', 1);
INSERT INTO `master_distrito` VALUES (13, 'Jesús María', '150113', 1);
INSERT INTO `master_distrito` VALUES (14, 'La Molina', '150114', 1);
INSERT INTO `master_distrito` VALUES (15, 'La Victoria', '150115', 1);
INSERT INTO `master_distrito` VALUES (16, 'Lince', '150116', 1);
INSERT INTO `master_distrito` VALUES (17, 'Los Olivos', '150117', 1);
INSERT INTO `master_distrito` VALUES (18, 'Lurigancho', '150118', 1);
INSERT INTO `master_distrito` VALUES (19, 'Lurín', '150119', 1);
INSERT INTO `master_distrito` VALUES (20, 'Magdalena del Mar', '150120', 1);
INSERT INTO `master_distrito` VALUES (21, 'Miraflores', '150121', 1);
INSERT INTO `master_distrito` VALUES (22, 'Pachacámac', '150122', 1);
INSERT INTO `master_distrito` VALUES (23, 'Pucusana', '150123', 1);
INSERT INTO `master_distrito` VALUES (24, 'Pueblo Libre', '150124', 1);
INSERT INTO `master_distrito` VALUES (25, 'Puente Piedra', '150125', 1);
INSERT INTO `master_distrito` VALUES (26, 'Punta Hermosa', '150126', 1);
INSERT INTO `master_distrito` VALUES (27, 'Punta Negra', '150127', 1);
INSERT INTO `master_distrito` VALUES (28, 'Rímac', '150128', 1);
INSERT INTO `master_distrito` VALUES (29, 'San Bartolo', '150129', 1);
INSERT INTO `master_distrito` VALUES (30, 'San Borja', '150130', 1);
INSERT INTO `master_distrito` VALUES (31, 'San Isidro', '150131', 1);
INSERT INTO `master_distrito` VALUES (32, 'San Juan de Lurigancho', '150132', 1);
INSERT INTO `master_distrito` VALUES (33, 'San Juan de Miraflores', '150133', 1);
INSERT INTO `master_distrito` VALUES (34, 'San Luis', '150134', 1);
INSERT INTO `master_distrito` VALUES (35, 'San Martín de Porres', '150135', 1);
INSERT INTO `master_distrito` VALUES (36, 'San Miguel', '150136', 1);
INSERT INTO `master_distrito` VALUES (37, 'Santa Anita', '150137', 1);
INSERT INTO `master_distrito` VALUES (38, 'Santa María del Mar', '150138', 1);
INSERT INTO `master_distrito` VALUES (39, 'Santa Rosa', '150139', 1);
INSERT INTO `master_distrito` VALUES (40, 'Santiago de Surco', '150140', 1);
INSERT INTO `master_distrito` VALUES (41, 'Surquillo', '150141', 1);
INSERT INTO `master_distrito` VALUES (42, 'Villa El Salvador', '150142', 1);
INSERT INTO `master_distrito` VALUES (43, 'Villa María del Triunfo', '150143', 1);
INSERT INTO `master_distrito` VALUES (44, 'Callao', '150701', 2);
INSERT INTO `master_distrito` VALUES (45, 'Bellavista', '150702', 2);
INSERT INTO `master_distrito` VALUES (46, 'Carmen de la Legua Reynoso', '150703', 2);
INSERT INTO `master_distrito` VALUES (47, 'La Perla', '150704', 2);
INSERT INTO `master_distrito` VALUES (48, 'La Punta', '150705', 2);
INSERT INTO `master_distrito` VALUES (49, 'Ventanilla', '150706', 2);
INSERT INTO `master_distrito` VALUES (50, 'Arequipa', '040101', 12);
INSERT INTO `master_distrito` VALUES (51, 'Alto Selva Alegre', '040102', 12);
INSERT INTO `master_distrito` VALUES (52, 'Cayma', '040103', 12);
INSERT INTO `master_distrito` VALUES (53, 'Cerro Colorado', '040104', 12);
INSERT INTO `master_distrito` VALUES (54, 'Characato', '040105', 12);
INSERT INTO `master_distrito` VALUES (55, 'Chiguata', '040106', 12);
INSERT INTO `master_distrito` VALUES (56, 'Jacobo Hunter', '040107', 12);
INSERT INTO `master_distrito` VALUES (57, 'La Joya', '040108', 12);
INSERT INTO `master_distrito` VALUES (58, 'Mariano Melgar', '040109', 12);
INSERT INTO `master_distrito` VALUES (59, 'Miraflores', '040110', 12);
INSERT INTO `master_distrito` VALUES (60, 'Mollebaya', '040111', 12);
INSERT INTO `master_distrito` VALUES (61, 'Paucarpata', '040112', 12);
INSERT INTO `master_distrito` VALUES (62, 'Pocsi', '040113', 12);
INSERT INTO `master_distrito` VALUES (63, 'Polobaya', '040114', 12);
INSERT INTO `master_distrito` VALUES (64, 'Quequeña', '040115', 12);
INSERT INTO `master_distrito` VALUES (65, 'Sabandia', '040116', 12);
INSERT INTO `master_distrito` VALUES (66, 'Sachaca', '040117', 12);
INSERT INTO `master_distrito` VALUES (67, 'San Juan de Siguas', '040118', 12);
INSERT INTO `master_distrito` VALUES (68, 'San Juan de Tarucani', '040119', 12);
INSERT INTO `master_distrito` VALUES (69, 'Santa Isabel de Siguas', '040120', 12);
INSERT INTO `master_distrito` VALUES (70, 'Santa Rita de Siguas', '040121', 12);
INSERT INTO `master_distrito` VALUES (71, 'Socabaya', '040122', 12);
INSERT INTO `master_distrito` VALUES (72, 'Tiabaya', '040123', 12);
INSERT INTO `master_distrito` VALUES (73, 'Uchumayo', '040124', 12);
INSERT INTO `master_distrito` VALUES (74, 'Vitor', '040125', 12);
INSERT INTO `master_distrito` VALUES (75, 'Yanahuara', '040126', 12);
INSERT INTO `master_distrito` VALUES (76, 'Yarabamba', '040127', 12);
INSERT INTO `master_distrito` VALUES (77, 'Yura', '040128', 12);
INSERT INTO `master_distrito` VALUES (78, 'Cusco', '080101', 20);
INSERT INTO `master_distrito` VALUES (79, 'Ccorca', '080102', 20);
INSERT INTO `master_distrito` VALUES (80, 'Poroy', '080103', 20);
INSERT INTO `master_distrito` VALUES (81, 'San Jerónimo', '080104', 20);
INSERT INTO `master_distrito` VALUES (82, 'San Sebastian', '080105', 20);
INSERT INTO `master_distrito` VALUES (83, 'Santiago', '080106', 20);
INSERT INTO `master_distrito` VALUES (84, 'Saylla', '080107', 20);
INSERT INTO `master_distrito` VALUES (85, 'Wanchaq', '080108', 20);
INSERT INTO `master_distrito` VALUES (86, 'Trujillo', '130101', 33);
INSERT INTO `master_distrito` VALUES (87, 'El Porvenir', '130102', 33);
INSERT INTO `master_distrito` VALUES (88, 'Florencia de Mora', '130103', 33);
INSERT INTO `master_distrito` VALUES (89, 'Huanchaco', '130104', 33);
INSERT INTO `master_distrito` VALUES (90, 'La Esperanza', '130105', 33);
INSERT INTO `master_distrito` VALUES (91, 'Laredo', '130106', 33);
INSERT INTO `master_distrito` VALUES (92, 'Moche', '130107', 33);
INSERT INTO `master_distrito` VALUES (93, 'Poroto', '130108', 33);
INSERT INTO `master_distrito` VALUES (94, 'Salaverry', '130109', 33);
INSERT INTO `master_distrito` VALUES (95, 'Simbal', '130110', 33);
INSERT INTO `master_distrito` VALUES (96, 'Victor Larco Herrera', '130111', 33);
INSERT INTO `master_distrito` VALUES (97, 'Piura', '200101', 45);
INSERT INTO `master_distrito` VALUES (98, 'Castilla', '200102', 45);
INSERT INTO `master_distrito` VALUES (99, 'Catacaos', '200103', 45);
INSERT INTO `master_distrito` VALUES (100, 'Cura Mori', '200104', 45);
INSERT INTO `master_distrito` VALUES (101, 'El Tallán', '200105', 45);
INSERT INTO `master_distrito` VALUES (102, 'La Arena', '200106', 45);
INSERT INTO `master_distrito` VALUES (103, 'La Unión', '200107', 45);
INSERT INTO `master_distrito` VALUES (104, 'Las Lomas', '200108', 45);
INSERT INTO `master_distrito` VALUES (105, 'Tambo Grande', '200109', 45);
INSERT INTO `master_distrito` VALUES (106, 'Veintiseis de Octubre', '200110', 45);

-- ----------------------------
-- Table structure for master_experiencialaboral
-- ----------------------------
DROP TABLE IF EXISTS `master_experiencialaboral`;
CREATE TABLE `master_experiencialaboral`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tipo_experiencia` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `tipo_entidad` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `nombre_entidad` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `cargo` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NULL DEFAULT NULL,
  `salario` decimal(10, 2) NULL DEFAULT NULL,
  `motivo_salida` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `logros` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `responsabilidades` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `supervisor` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `telefono_referencia` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `observaciones` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `cv_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `master_expe_cv_id_4e93cf_idx`(`cv_id` ASC) USING BTREE,
  INDEX `master_expe_tipo_ex_1752b7_idx`(`tipo_experiencia` ASC) USING BTREE,
  INDEX `master_expe_fecha_i_1a00a0_idx`(`fecha_inicio` ASC) USING BTREE,
  CONSTRAINT `master_experiencialaboral_cv_id_791ffa6d_fk_master_cv_id` FOREIGN KEY (`cv_id`) REFERENCES `master_cv` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_experiencialaboral
-- ----------------------------
INSERT INTO `master_experiencialaboral` VALUES (1, 'GENERAL', 'PUBLICO', 'UNIVERSIDAD NACIONAL HERMILIO VALDIZAN (UNHEVAL)', 'Programador', '2025-09-10', '2025-09-17', 1500.00, 'Personal', 'logro', 'r', 'Juan Perez', '942558552', 'Ninguna', '2025-09-18 03:33:47.683194', '2025-09-18 03:33:47.683194', 1);
INSERT INTO `master_experiencialaboral` VALUES (3, 'LABORAL', 'EMPRESA', 'UNIVERSIDAD NACIONAL HERMILIO VALDIZAN (UNHEVAL)', 'Programador', '2025-09-02', '2025-09-24', 1600.00, 'DESPIDO', 'qwe', 'qwe', 'Juan Perez', '942558552', 'qwe', '2025-09-24 18:22:19.103829', '2025-09-24 18:22:19.103829', 2);

-- ----------------------------
-- Table structure for master_formacionacademica
-- ----------------------------
DROP TABLE IF EXISTS `master_formacionacademica`;
CREATE TABLE `master_formacionacademica`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `grado` varchar(30) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `especialidad` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `centro_estudio` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `ciudad` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `pais` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `fecha_expedicion` date NOT NULL,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `promedio` decimal(4, 2) NULL DEFAULT NULL,
  `observaciones` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `cv_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `master_form_cv_id_4f4989_idx`(`cv_id` ASC) USING BTREE,
  INDEX `master_form_grado_9df1cd_idx`(`grado` ASC) USING BTREE,
  CONSTRAINT `master_formacionacademica_cv_id_e88f28ab_fk_master_cv_id` FOREIGN KEY (`cv_id`) REFERENCES `master_cv` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_formacionacademica
-- ----------------------------
INSERT INTO `master_formacionacademica` VALUES (2, 'LICENCIADO', 'Ingeniería de Sistemas', 'Universidad Nacional de Ingeniería', 'Lima', 'Perú', '2025-09-26', '2025-09-02', '2025-09-17', 18.00, 'Ninguno', '2025-09-18 03:32:52.503691', '2025-09-18 03:32:52.503691', 1);
INSERT INTO `master_formacionacademica` VALUES (3, 'INGENIERO', 'Ingeniería de Sistemas', 'Universidad Nacional de Ingeniería', 'Lima', 'Perú', '2025-09-26', '2025-09-24', '2025-09-26', 17.00, 'qwe', '2025-09-24 17:44:22.068458', '2025-09-24 17:52:19.441092', 2);
INSERT INTO `master_formacionacademica` VALUES (5, 'MAESTRO', 'Ingeniería de Sistemas', 'Universidad Nacional de Ingeniería', 'Lima', 'Perú', '2025-09-26', '2025-09-24', '2025-09-26', 15.00, 'Ninguna ', '2025-09-24 17:55:19.349127', '2025-09-24 17:55:19.349127', 2);

-- ----------------------------
-- Table structure for master_persona
-- ----------------------------
DROP TABLE IF EXISTS `master_persona`;
CREATE TABLE `master_persona`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `tipo_documento` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `numero_documento` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `apellido_paterno` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `apellido_materno` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `nombres` varchar(150) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `fecha_nacimiento` date NOT NULL,
  `sexo` varchar(1) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `estado_civil` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `celular` varchar(15) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `email` varchar(254) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `direccion` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `departamento_id` bigint NULL DEFAULT NULL,
  `distrito_id` bigint NULL DEFAULT NULL,
  `provincia_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `numero_documento`(`numero_documento` ASC) USING BTREE,
  INDEX `master_pers_numero__3c49c2_idx`(`numero_documento` ASC) USING BTREE,
  INDEX `master_pers_email_5853cd_idx`(`email` ASC) USING BTREE,
  INDEX `master_pers_fecha_c_8ec37d_idx`(`fecha_creacion` ASC) USING BTREE,
  INDEX `master_persona_departamento_id_f7df44b9_fk_master_de`(`departamento_id` ASC) USING BTREE,
  INDEX `master_persona_distrito_id_b20120e1_fk_master_distrito_id`(`distrito_id` ASC) USING BTREE,
  INDEX `master_persona_provincia_id_9c14d7f1_fk_master_provincia_id`(`provincia_id` ASC) USING BTREE,
  CONSTRAINT `master_persona_departamento_id_f7df44b9_fk_master_de` FOREIGN KEY (`departamento_id`) REFERENCES `master_departamento` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `master_persona_distrito_id_b20120e1_fk_master_distrito_id` FOREIGN KEY (`distrito_id`) REFERENCES `master_distrito` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `master_persona_provincia_id_9c14d7f1_fk_master_provincia_id` FOREIGN KEY (`provincia_id`) REFERENCES `master_provincia` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_persona
-- ----------------------------
INSERT INTO `master_persona` VALUES (1, 'DNI', '70864821', 'PEÑA', 'CONDEZO', 'Jeff Carlos', '2025-03-05', 'M', 'SOLTERO', '983488611', 'jeff_carlos_3040@hotmail.com', 'Urb santa maria MZ H LT 5', '2025-09-17 18:35:16.652231', '2025-09-17 18:40:54.454309', 15, 44, 2);
INSERT INTO `master_persona` VALUES (2, 'DNI', '70255878', 'test', 'TEST', 'TEST', '2025-09-24', 'M', '', '421213', 'jeff_carlos_3040@hotmail.com', 'Urb santa maria MZ H LT 4', '2025-09-24 17:25:09.413494', '2025-09-24 17:25:09.413494', 15, 8, 1);
INSERT INTO `master_persona` VALUES (4, 'DNI', '12345678', 'test', 'TEST', 'TEST', '2025-09-24', 'M', '', '421213', 'jeff_carlos_3040@hotmail.com', 'Urb santa maria MZ H LT 4', '2025-09-24 17:26:29.865424', '2025-09-24 17:26:29.865424', 15, 5, 1);

-- ----------------------------
-- Table structure for master_postulacion
-- ----------------------------
DROP TABLE IF EXISTS `master_postulacion`;
CREATE TABLE `master_postulacion`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `fecha_postulacion` datetime(6) NOT NULL,
  `estado_postulacion` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `experiencia_anios` int UNSIGNED NOT NULL,
  `nivel_educacion` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `institucion_educacion` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `observaciones` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL,
  `fecha_creacion` datetime(6) NOT NULL,
  `fecha_actualizacion` datetime(6) NOT NULL,
  `convocatoria_id` bigint NOT NULL,
  `persona_id` bigint NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `master_postulacion_persona_id_convocatoria_id_1c96a293_uniq`(`persona_id` ASC, `convocatoria_id` ASC) USING BTREE,
  INDEX `master_postulacion_convocatoria_id_66a29a1b_fk_master_co`(`convocatoria_id` ASC) USING BTREE,
  INDEX `master_post_estado__1b1c20_idx`(`estado_postulacion` ASC) USING BTREE,
  INDEX `master_post_fecha_p_9e599b_idx`(`fecha_postulacion` ASC) USING BTREE,
  INDEX `master_post_persona_c3e838_idx`(`persona_id` ASC, `convocatoria_id` ASC) USING BTREE,
  CONSTRAINT `master_postulacion_convocatoria_id_66a29a1b_fk_master_co` FOREIGN KEY (`convocatoria_id`) REFERENCES `master_convocatoria` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `master_postulacion_persona_id_29d02a90_fk_master_persona_id` FOREIGN KEY (`persona_id`) REFERENCES `master_persona` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_postulacion
-- ----------------------------
INSERT INTO `master_postulacion` VALUES (1, '2025-09-18 03:45:30.962694', 'APROBADO', 0, NULL, NULL, 'Ninguno', '2025-09-18 03:45:30.963759', '2025-09-18 20:59:27.351175', 2, 1);

-- ----------------------------
-- Table structure for master_provincia
-- ----------------------------
DROP TABLE IF EXISTS `master_provincia`;
CREATE TABLE `master_provincia`  (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `codigo` varchar(4) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `departamento_id` bigint NOT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `master_provincia_codigo_departamento_id_fdbd1239_uniq`(`codigo` ASC, `departamento_id` ASC) USING BTREE,
  INDEX `master_provincia_departamento_id_fe83df55_fk_master_de`(`departamento_id` ASC) USING BTREE,
  CONSTRAINT `master_provincia_departamento_id_fe83df55_fk_master_de` FOREIGN KEY (`departamento_id`) REFERENCES `master_departamento` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 53 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of master_provincia
-- ----------------------------
INSERT INTO `master_provincia` VALUES (1, 'Lima', '1501', 15);
INSERT INTO `master_provincia` VALUES (2, 'Callao', '1507', 15);
INSERT INTO `master_provincia` VALUES (3, 'Barranca', '1502', 15);
INSERT INTO `master_provincia` VALUES (4, 'Cajatambo', '1503', 15);
INSERT INTO `master_provincia` VALUES (5, 'Canta', '1504', 15);
INSERT INTO `master_provincia` VALUES (6, 'Cañete', '1505', 15);
INSERT INTO `master_provincia` VALUES (7, 'Huaral', '1506', 15);
INSERT INTO `master_provincia` VALUES (8, 'Huarochirí', '1508', 15);
INSERT INTO `master_provincia` VALUES (9, 'Huaura', '1509', 15);
INSERT INTO `master_provincia` VALUES (10, 'Oyón', '1510', 15);
INSERT INTO `master_provincia` VALUES (11, 'Yauyos', '1511', 15);
INSERT INTO `master_provincia` VALUES (12, 'Arequipa', '0401', 4);
INSERT INTO `master_provincia` VALUES (13, 'Camaná', '0402', 4);
INSERT INTO `master_provincia` VALUES (14, 'Caravelí', '0403', 4);
INSERT INTO `master_provincia` VALUES (15, 'Castilla', '0404', 4);
INSERT INTO `master_provincia` VALUES (16, 'Caylloma', '0405', 4);
INSERT INTO `master_provincia` VALUES (17, 'Condesuyos', '0406', 4);
INSERT INTO `master_provincia` VALUES (18, 'Islay', '0407', 4);
INSERT INTO `master_provincia` VALUES (19, 'La Uniòn', '0408', 4);
INSERT INTO `master_provincia` VALUES (20, 'Cusco', '0801', 8);
INSERT INTO `master_provincia` VALUES (21, 'Acomayo', '0802', 8);
INSERT INTO `master_provincia` VALUES (22, 'Anta', '0803', 8);
INSERT INTO `master_provincia` VALUES (23, 'Calca', '0804', 8);
INSERT INTO `master_provincia` VALUES (24, 'Canas', '0805', 8);
INSERT INTO `master_provincia` VALUES (25, 'Canchis', '0806', 8);
INSERT INTO `master_provincia` VALUES (26, 'Chumbivilcas', '0807', 8);
INSERT INTO `master_provincia` VALUES (27, 'Espinar', '0808', 8);
INSERT INTO `master_provincia` VALUES (28, 'La Convención', '0809', 8);
INSERT INTO `master_provincia` VALUES (29, 'Paruro', '0810', 8);
INSERT INTO `master_provincia` VALUES (30, 'Paucartambo', '0811', 8);
INSERT INTO `master_provincia` VALUES (31, 'Quispicanchi', '0812', 8);
INSERT INTO `master_provincia` VALUES (32, 'Urubamba', '0813', 8);
INSERT INTO `master_provincia` VALUES (33, 'Trujillo', '1301', 13);
INSERT INTO `master_provincia` VALUES (34, 'Ascope', '1302', 13);
INSERT INTO `master_provincia` VALUES (35, 'Bolívar', '1303', 13);
INSERT INTO `master_provincia` VALUES (36, 'Chepén', '1304', 13);
INSERT INTO `master_provincia` VALUES (37, 'Gran Chimú', '1305', 13);
INSERT INTO `master_provincia` VALUES (38, 'Julcán', '1306', 13);
INSERT INTO `master_provincia` VALUES (39, 'Otuzco', '1307', 13);
INSERT INTO `master_provincia` VALUES (40, 'Pacasmayo', '1308', 13);
INSERT INTO `master_provincia` VALUES (41, 'Pataz', '1309', 13);
INSERT INTO `master_provincia` VALUES (42, 'Sánchez Carrión', '1310', 13);
INSERT INTO `master_provincia` VALUES (43, 'Santiago de Chuco', '1311', 13);
INSERT INTO `master_provincia` VALUES (44, 'Virú', '1312', 13);
INSERT INTO `master_provincia` VALUES (45, 'Piura', '2001', 20);
INSERT INTO `master_provincia` VALUES (46, 'Ayabaca', '2002', 20);
INSERT INTO `master_provincia` VALUES (47, 'Huancabamba', '2003', 20);
INSERT INTO `master_provincia` VALUES (48, 'Morropón', '2004', 20);
INSERT INTO `master_provincia` VALUES (49, 'Paita', '2005', 20);
INSERT INTO `master_provincia` VALUES (50, 'Sullana', '2006', 20);
INSERT INTO `master_provincia` VALUES (51, 'Talara', '2007', 20);
INSERT INTO `master_provincia` VALUES (52, 'Sechura', '2008', 20);

SET FOREIGN_KEY_CHECKS = 1;

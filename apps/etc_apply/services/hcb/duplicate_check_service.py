# -*- coding: utf-8 -*-
"""
货车ETC防重复申办检查服务
处理重复申办问题：检查、临时修改状态、恢复状态
"""

import json
import time
from typing import Dict, Any, List, Optional, Tuple
from common.mysql_util import MySQLUtil
from apps.etc_apply.services.hcb.truck_core_service import TruckCoreService
from apps.etc_apply.services.rtx.log_service import LogService


class DuplicateCheckService:
    """防重复申办检查服务"""
    
    def __init__(self):
        self.log_service = LogService("duplicate_check")
        self.backup_records = []  # 存储需要恢复的记录
        
    def check_user_existing_applications(self, user_info: Dict[str, Any]) -> Tuple[bool, List[Dict]]:
        """
        检查用户是否已有ETC申办记录（增强版：带调试日志和优化查询策略）
        :param user_info: 用户五要素信息 {name, phone, id_code, car_num, vehicle_color}
        :return: (是否有记录, 记录列表)
        """
        try:
            # 参数验证和标准化
            phone = user_info.get('phone', '').strip()
            id_code = user_info.get('id_code', '').strip()
            car_num = user_info.get('car_num', '').strip()
            name = user_info.get('name', '').strip()
            vehicle_color = user_info.get('vehicle_color', '').strip()
            
            self.log_service.info("🔍 开始检查用户是否已有ETC申办记录")
            self.log_service.info(f"📋 检查参数: 手机号={phone}, 身份证={id_code}, 车牌={car_num}, 姓名={name}, 车牌颜色={vehicle_color}")
            
            # 检查参数完整性
            if not any([phone, id_code, car_num, name]):
                self.log_service.warning("⚠️ 所有关键参数都为空，无法进行重复检查")
                return False, []
            
            # 获取数据库连接配置
            conf = TruckCoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            
            existing_records = []
            
            # 1. 检查货车用户表 hcb_truckuser
            self.log_service.info("🔍 检查货车用户表 hcb_truckuser")
            truckuser_records = self._check_truckuser_table_enhanced(db, user_info)
            if truckuser_records:
                existing_records.extend(truckuser_records)
                self.log_service.info(f"✅ 货车用户表找到{len(truckuser_records)}条记录")
            else:
                self.log_service.info("✅ 货车用户表无匹配记录")
                
            # 2. 检查申办记录表 hcb_trucketcapply  
            self.log_service.info("🔍 检查申办记录表 hcb_trucketcapply")
            apply_records = self._check_trucketcapply_table_enhanced(db, user_info)
            if apply_records:
                existing_records.extend(apply_records)
                self.log_service.info(f"✅ 申办记录表找到{len(apply_records)}条记录")
            else:
                self.log_service.info("✅ 申办记录表无匹配记录")
            
            db.close()
            
            has_existing = len(existing_records) > 0
            if has_existing:
                self.log_service.warning(f"⚠️ 发现用户已有{len(existing_records)}条ETC相关记录")
                for i, record in enumerate(existing_records, 1):
                    self.log_service.info(f"  记录{i}: 表={record['table']}, 车牌={record['car_num']}, 匹配类型={record['match_type']}")
            else:
                self.log_service.info("✅ 用户无ETC申办记录，可以正常申办")
                
            return has_existing, existing_records
            
        except Exception as e:
            self.log_service.error(f"❌ 检查用户ETC记录失败: {str(e)}")
            raise e
    
    def _check_truckuser_table(self, db: MySQLUtil, user_info: Dict[str, Any]) -> List[Dict]:
        """检查货车用户表"""
        try:
            # 通过五要素查询：手机号、身份证号、车牌号、姓名
            # 🔥 临时修改：移除了 AND STATUS != '4' 的过滤条件，查询所有状态的记录
            query = """
                SELECT 
                    TRUCKUSER_ID, CAR_NUM, NAME, PHONE, ID_CODE, STATUS, 
                    OBU_NO, ETC_SN, ETCSTATUS, CREATE_TIME, VEHICLECOLOR
                FROM hcb.hcb_truckuser 
                WHERE (PHONE = %s OR ID_CODE = %s OR CAR_NUM = %s OR NAME = %s)
                ORDER BY CREATE_TIME DESC
            """
            
            params = (
                user_info.get('phone', ''),
                user_info.get('id_code', ''), 
                user_info.get('car_num', ''),
                user_info.get('name', '')
            )
            
            results = db.query(query, params)
            
            records = []
            for result in results:
                records.append({
                    'table': 'hcb_truckuser',
                    'id': result.get('TRUCKUSER_ID'),
                    'car_num': result.get('CAR_NUM'),
                    'name': result.get('NAME'),
                    'phone': result.get('PHONE'),
                    'id_code': result.get('ID_CODE'),
                    'status': result.get('STATUS'),
                    'obu_no': result.get('OBU_NO'),
                    'etc_sn': result.get('ETC_SN'),
                    'etc_status': result.get('ETCSTATUS'),
                    'create_time': result.get('CREATE_TIME'),
                    'vehicle_color': result.get('VEHICLECOLOR'),
                    'current_status': result.get('STATUS'),
                    'match_type': self._determine_match_type(user_info, result)
                })
                
            return records
            
        except Exception as e:
            self.log_service.error(f"检查hcb_truckuser表失败: {str(e)}")
            return []
    
    def _check_trucketcapply_table(self, db: MySQLUtil, user_info: Dict[str, Any]) -> List[Dict]:
        """检查申办记录表"""
        try:
            # 通过五要素查询申办记录
            # 🔥 临时修改：移除了 AND ETCSTATUS IN (...) 的过滤条件，查询所有状态的记录
            query = """
                SELECT 
                    TRUCKETCAPPLY_ID, CAR_NUM, CARD_HOLDER, PHONE, IDCODE, 
                    ETCSTATUS, ETC_SN, OBU_NO, CREATE_TIME, VEHICLECOLOR
                FROM hcb.hcb_trucketcapply 
                WHERE (PHONE = %s OR IDCODE = %s OR CAR_NUM = %s OR CARD_HOLDER = %s)
                ORDER BY CREATE_TIME DESC
            """
            
            params = (
                user_info.get('phone', ''),
                user_info.get('id_code', ''),
                user_info.get('car_num', ''), 
                user_info.get('name', '')
            )
            
            results = db.query(query, params)
            
            records = []
            for result in results:
                records.append({
                    'table': 'hcb_trucketcapply',
                    'id': result.get('TRUCKETCAPPLY_ID'),
                    'car_num': result.get('CAR_NUM'),
                    'name': result.get('CARD_HOLDER'),
                    'phone': result.get('PHONE'),
                    'id_code': result.get('IDCODE'),
                    'etc_status': result.get('ETCSTATUS'),
                    'obu_no': result.get('OBU_NO'),
                    'etc_sn': result.get('ETC_SN'),
                    'create_time': result.get('CREATE_TIME'),
                    'vehicle_color': result.get('VEHICLECOLOR'),
                    'current_status': result.get('ETCSTATUS'),
                    'match_type': self._determine_match_type_apply(user_info, result)
                })
                
            return records
            
        except Exception as e:
            self.log_service.error(f"检查hcb_trucketcapply表失败: {str(e)}")
            return []
    
    def _check_truckuser_table_enhanced(self, db: MySQLUtil, user_info: Dict[str, Any]) -> List[Dict]:
        """检查货车用户表（增强版：分级匹配策略）"""
        try:
            phone = user_info.get('phone', '').strip()
            id_code = user_info.get('id_code', '').strip()
            car_num = user_info.get('car_num', '').strip()
            name = user_info.get('name', '').strip()
            
            records = []
            
            # 优先级1: 身份证+手机号精确匹配（最可靠）
            if phone and id_code:
                query = """
                    SELECT 
                        TRUCKUSER_ID, CAR_NUM, NAME, PHONE, ID_CODE, STATUS, 
                        OBU_NO, ETC_SN, ETCSTATUS, CREATE_TIME, VEHICLECOLOR
                    FROM hcb.hcb_truckuser 
                    WHERE PHONE = %s AND ID_CODE = %s AND STATUS != '4'
                    ORDER BY CREATE_TIME DESC
                """
                results = db.query(query, (phone, id_code))
                for result in results:
                    records.append({
                        'table': 'hcb_truckuser',
                        'id': result.get('TRUCKUSER_ID'),
                        'car_num': result.get('CAR_NUM'),
                        'name': result.get('NAME'),
                        'phone': result.get('PHONE'),
                        'id_code': result.get('ID_CODE'),
                        'status': result.get('STATUS'),
                        'obu_no': result.get('OBU_NO'),
                        'etc_sn': result.get('ETC_SN'),
                        'etc_status': result.get('ETCSTATUS'),
                        'create_time': result.get('CREATE_TIME'),
                        'vehicle_color': result.get('VEHICLECOLOR'),
                        'current_status': result.get('STATUS'),
                        'match_type': '身份证+手机号(精确)',
                        'confidence': 'high'
                    })
                self.log_service.info(f"📞 身份证+手机号匹配到{len(results)}条货车用户记录")
            
            # 优先级2: 车牌号+姓名匹配（中等可靠）
            if car_num and name:
                existing_ids = [r['id'] for r in records]
                id_filter = f"AND TRUCKUSER_ID NOT IN ({','.join(['%s'] * len(existing_ids))})" if existing_ids else ""
                
                query = f"""
                    SELECT 
                        TRUCKUSER_ID, CAR_NUM, NAME, PHONE, ID_CODE, STATUS, 
                        OBU_NO, ETC_SN, ETCSTATUS, CREATE_TIME, VEHICLECOLOR
                    FROM hcb.hcb_truckuser 
                    WHERE CAR_NUM = %s AND NAME = %s AND STATUS != '4' {id_filter}
                    ORDER BY CREATE_TIME DESC
                """
                
                params = [car_num, name] + existing_ids
                results = db.query(query, params)
                for result in results:
                    records.append({
                        'table': 'hcb_truckuser',
                        'id': result.get('TRUCKUSER_ID'),
                        'car_num': result.get('CAR_NUM'),
                        'name': result.get('NAME'),
                        'phone': result.get('PHONE'),
                        'id_code': result.get('ID_CODE'),
                        'status': result.get('STATUS'),
                        'obu_no': result.get('OBU_NO'),
                        'etc_sn': result.get('ETC_SN'),
                        'etc_status': result.get('ETCSTATUS'),
                        'create_time': result.get('CREATE_TIME'),
                        'vehicle_color': result.get('VEHICLECOLOR'),
                        'current_status': result.get('STATUS'),
                        'match_type': '车牌+姓名(中等)',
                        'confidence': 'medium'
                    })
                self.log_service.info(f"🚗 车牌+姓名匹配到{len(results)}条新的货车用户记录")
                
            return records
            
        except Exception as e:
            self.log_service.error(f"❌ 检查hcb_truckuser表失败: {str(e)}")
            return []
    
    def _check_trucketcapply_table_enhanced(self, db: MySQLUtil, user_info: Dict[str, Any]) -> List[Dict]:
        """检查申办记录表（增强版：分级匹配策略）"""
        try:
            phone = user_info.get('phone', '').strip()
            id_code = user_info.get('id_code', '').strip()
            car_num = user_info.get('car_num', '').strip()
            name = user_info.get('name', '').strip()
            
            records = []
            
            # 优先级1: 身份证+手机号精确匹配（最可靠）
            if phone and id_code:
                query = """
                    SELECT 
                        TRUCKETCAPPLY_ID, CAR_NUM, CARD_HOLDER, PHONE, IDCODE, 
                        ETCSTATUS, ETC_SN, OBU_NO, CREATE_TIME, VEHICLECOLOR
                    FROM hcb.hcb_trucketcapply 
                    WHERE PHONE = %s AND IDCODE = %s AND ETCSTATUS NOT IN ('8', '10')
                    ORDER BY CREATE_TIME DESC
                """
                results = db.query(query, (phone, id_code))
                for result in results:
                    records.append({
                        'table': 'hcb_trucketcapply',
                        'id': result.get('TRUCKETCAPPLY_ID'),
                        'car_num': result.get('CAR_NUM'),
                        'name': result.get('CARD_HOLDER'),
                        'phone': result.get('PHONE'),
                        'id_code': result.get('IDCODE'),
                        'etc_status': result.get('ETCSTATUS'),
                        'obu_no': result.get('OBU_NO'),
                        'etc_sn': result.get('ETC_SN'),
                        'create_time': result.get('CREATE_TIME'),
                        'vehicle_color': result.get('VEHICLECOLOR'),
                        'current_status': result.get('ETCSTATUS'),
                        'match_type': '身份证+手机号(精确)',
                        'confidence': 'high'
                    })
                self.log_service.info(f"📞 身份证+手机号匹配到{len(results)}条申办记录")
            
            # 优先级2: 车牌号+姓名匹配（中等可靠）
            if car_num and name:
                existing_ids = [r['id'] for r in records]
                id_filter = f"AND TRUCKETCAPPLY_ID NOT IN ({','.join(['%s'] * len(existing_ids))})" if existing_ids else ""
                
                query = f"""
                    SELECT 
                        TRUCKETCAPPLY_ID, CAR_NUM, CARD_HOLDER, PHONE, IDCODE, 
                        ETCSTATUS, ETC_SN, OBU_NO, CREATE_TIME, VEHICLECOLOR
                    FROM hcb.hcb_trucketcapply 
                    WHERE CAR_NUM = %s AND CARD_HOLDER = %s AND ETCSTATUS NOT IN ('8', '10') {id_filter}
                    ORDER BY CREATE_TIME DESC
                """
                
                params = [car_num, name] + existing_ids
                results = db.query(query, params)
                for result in results:
                    records.append({
                        'table': 'hcb_trucketcapply',
                        'id': result.get('TRUCKETCAPPLY_ID'),
                        'car_num': result.get('CAR_NUM'),
                        'name': result.get('CARD_HOLDER'),
                        'phone': result.get('PHONE'),
                        'id_code': result.get('IDCODE'),
                        'etc_status': result.get('ETCSTATUS'),
                        'obu_no': result.get('OBU_NO'),
                        'etc_sn': result.get('ETC_SN'),
                        'create_time': result.get('CREATE_TIME'),
                        'vehicle_color': result.get('VEHICLECOLOR'),
                        'current_status': result.get('ETCSTATUS'),
                        'match_type': '车牌+姓名(中等)',
                        'confidence': 'medium'
                    })
                self.log_service.info(f"🚗 车牌+姓名匹配到{len(results)}条新的申办记录")
                
            return records
            
        except Exception as e:
            self.log_service.error(f"❌ 检查hcb_trucketcapply表失败: {str(e)}")
            return []
    
    def _determine_match_type(self, user_info: Dict, record: Dict) -> str:
        """判断匹配类型（货车用户表）"""
        matches = []
        if user_info.get('phone') == record.get('PHONE'):
            matches.append('手机号')
        if user_info.get('id_code') == record.get('ID_CODE'):
            matches.append('身份证')
        if user_info.get('car_num') == record.get('CAR_NUM'):
            matches.append('车牌号')
        if user_info.get('name') == record.get('NAME'):
            matches.append('姓名')
        return '+'.join(matches)
    
    def _determine_match_type_apply(self, user_info: Dict, record: Dict) -> str:
        """判断匹配类型（申办记录表）"""
        matches = []
        if user_info.get('phone') == record.get('PHONE'):
            matches.append('手机号')
        if user_info.get('id_code') == record.get('IDCODE'):
            matches.append('身份证')
        if user_info.get('car_num') == record.get('CAR_NUM'):
            matches.append('车牌号')
        if user_info.get('name') == record.get('CARD_HOLDER'):
            matches.append('姓名')
        return '+'.join(matches)
    
    def temporarily_modify_status_for_reapply(self, existing_records: List[Dict]) -> bool:
        """
        临时修改状态以允许重新申办
        只修改状态为"正常"的记录，跳过已经是异常状态的记录
        :param existing_records: 现有记录列表
        :return: 是否成功
        """
        try:
            self.log_service.info("开始临时修改车辆状态以允许重新申办")
            
            # 清空之前的备份记录
            self.backup_records = []
            
            # 获取数据库连接
            conf = TruckCoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            
            modified_count = 0
            
            for record in existing_records:
                # 🔥 临时修改：修改所有找到的记录，不进行状态过滤
                need_modify = True  # 强制修改所有记录
                
                if need_modify:
                    backup_record = self._create_backup_record(record)
                    
                    if record['table'] == 'hcb_truckuser':
                        # 修改货车用户表状态：STATUS改为'0'(暂无ETC状态)
                        success = self._modify_truckuser_status(db, record, '0')
                        if success:
                            modified_count += 1
                            self.backup_records.append(backup_record)
                            
                    elif record['table'] == 'hcb_trucketcapply':
                        # 修改申办记录表状态：ETCSTATUS改为'8'(已驳回)
                        success = self._modify_trucketcapply_status(db, record, '8')
                        if success:
                            modified_count += 1
                            self.backup_records.append(backup_record)
            
            db.close()
            
            self.log_service.info(f"状态修改结果（临时修改-无状态过滤）：成功修改{modified_count}条")
            
            if modified_count > 0:
                # 保存备份记录到文件（防止程序异常时数据丢失）
                self._save_backup_to_file()
                return True
            else:
                self.log_service.warning("没有找到任何需要处理的记录")
                return False
                
        except Exception as e:
            self.log_service.error(f"临时修改状态失败: {str(e)}")
            return False
    
    def _create_backup_record(self, record: Dict) -> Dict:
        """创建备份记录"""
        return {
            'table': record['table'],
            'id': record['id'],
            'original_status': record['current_status'],
            'car_num': record['car_num'],
            'backup_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'restored': False
        }
    
    def _modify_truckuser_status(self, db: MySQLUtil, record: Dict, new_status: str) -> bool:
        """修改货车用户表状态"""
        try:
            # 限制REMARK字段长度，避免数据过长错误
            # 只保留现有REMARK的最后150个字符，然后追加新的修改记录
            query = """
                UPDATE hcb.hcb_truckuser 
                SET STATUS = %s, 
                    REMARK = CONCAT(
                        RIGHT(IFNULL(REMARK, ''), 150), 
                        '[临时修改状态允许重新申办:', DATE_FORMAT(NOW(), '%%m-%%d %%H:%%i'), ']'
                    )
                WHERE TRUCKUSER_ID = %s
            """
            
            affected_rows = db.execute(query, (new_status, record['id']))
            
            if affected_rows > 0:
                self.log_service.info(f"成功修改货车用户表记录 {record['id']}: STATUS {record['current_status']} -> {new_status}")
                return True
            else:
                self.log_service.warning(f"修改货车用户表记录 {record['id']} 失败：无受影响的行")
                return False
                
        except Exception as e:
            self.log_service.error(f"修改货车用户表状态失败: {str(e)}")
            return False
    
    def _modify_trucketcapply_status(self, db: MySQLUtil, record: Dict, new_status: str) -> bool:
        """修改申办记录表状态"""
        try:
            # 限制CANCLE_MSG字段长度，避免数据过长错误
            # 只保留现有CANCLE_MSG的最后150个字符，然后追加新的修改记录
            query = """
                UPDATE hcb.hcb_trucketcapply 
                SET ETCSTATUS = %s, 
                    CANCLE_MSG = CONCAT(
                        RIGHT(IFNULL(CANCLE_MSG, ''), 150), 
                        '[临时修改状态允许重新申办:', DATE_FORMAT(NOW(), '%%m-%%d %%H:%%i'), ']'
                    )
                WHERE TRUCKETCAPPLY_ID = %s
            """
            
            affected_rows = db.execute(query, (new_status, record['id']))
            
            if affected_rows > 0:
                self.log_service.info(f"成功修改申办记录表记录 {record['id']}: ETCSTATUS {record['current_status']} -> {new_status}")
                return True
            else:
                self.log_service.warning(f"修改申办记录表记录 {record['id']} 失败：无受影响的行")
                return False
                
        except Exception as e:
            self.log_service.error(f"修改申办记录表状态失败: {str(e)}")
            return False
    
    def _save_backup_to_file(self):
        """保存备份记录到文件"""
        try:
            import os
            
            # 创建备份目录
            backup_dir = "temp/duplicate_check_backup"
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            backup_file = f"{backup_dir}/backup_{timestamp}.json"
            
            # 保存备份数据
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self.backup_records, f, ensure_ascii=False, indent=2)
                
            self.log_service.info(f"备份记录已保存到文件: {backup_file}")
            
        except Exception as e:
            self.log_service.error(f"保存备份文件失败: {str(e)}")
    
    def restore_original_status(self) -> bool:
        """
        恢复原始状态
        :return: 是否成功
        """
        try:
            if not self.backup_records:
                self.log_service.info("没有需要恢复的记录")
                return True
                
            self.log_service.info(f"开始恢复{len(self.backup_records)}条记录的原始状态")
            
            # 获取数据库连接
            conf = TruckCoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            
            restored_count = 0
            
            for backup_record in self.backup_records:
                if backup_record.get('restored', False):
                    continue  # 跳过已恢复的记录
                    
                success = False
                
                if backup_record['table'] == 'hcb_truckuser':
                    success = self._restore_truckuser_status(db, backup_record)
                elif backup_record['table'] == 'hcb_trucketcapply':
                    success = self._restore_trucketcapply_status(db, backup_record)
                
                if success:
                    backup_record['restored'] = True
                    backup_record['restore_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    restored_count += 1
            
            db.close()
            
            if restored_count > 0:
                self.log_service.info(f"成功恢复{restored_count}条记录的原始状态")
                # 更新备份文件
                self._save_backup_to_file()
                return True
            else:
                self.log_service.warning("没有成功恢复任何记录状态")
                return False
                
        except Exception as e:
            self.log_service.error(f"恢复原始状态失败: {str(e)}")
            return False
    
    def _restore_truckuser_status(self, db: MySQLUtil, backup_record: Dict) -> bool:
        """恢复货车用户表状态"""
        try:
            # 限制REMARK字段长度，避免数据过长错误
            # 只保留现有REMARK的最后150个字符，然后追加新的恢复记录
            query = """
                UPDATE hcb.hcb_truckuser 
                SET STATUS = %s, 
                    REMARK = CONCAT(
                        RIGHT(IFNULL(REMARK, ''), 150), 
                        '[恢复原状态:', DATE_FORMAT(NOW(), '%%m-%%d %%H:%%i'), ']'
                    )
                WHERE TRUCKUSER_ID = %s
            """
            
            affected_rows = db.execute(query, (backup_record['original_status'], backup_record['id']))
            
            if affected_rows > 0:
                self.log_service.info(f"成功恢复货车用户表记录 {backup_record['id']}: STATUS -> {backup_record['original_status']}")
                return True
            else:
                self.log_service.warning(f"恢复货车用户表记录 {backup_record['id']} 失败：无受影响的行")
                return False
                
        except Exception as e:
            self.log_service.error(f"恢复货车用户表状态失败: {str(e)}")
            return False
    
    def _restore_trucketcapply_status(self, db: MySQLUtil, backup_record: Dict) -> bool:
        """恢复申办记录表状态"""
        try:
            # 限制CANCLE_MSG字段长度，避免数据过长错误
            # 只保留现有CANCLE_MSG的最后150个字符，然后追加新的恢复记录
            query = """
                UPDATE hcb.hcb_trucketcapply 
                SET ETCSTATUS = %s, 
                    CANCLE_MSG = CONCAT(
                        RIGHT(IFNULL(CANCLE_MSG, ''), 150), 
                        '[恢复原状态:', DATE_FORMAT(NOW(), '%%m-%%d %%H:%%i'), ']'
                    )
                WHERE TRUCKETCAPPLY_ID = %s
            """
            
            affected_rows = db.execute(query, (backup_record['original_status'], backup_record['id']))
            
            if affected_rows > 0:
                self.log_service.info(f"成功恢复申办记录表记录 {backup_record['id']}: ETCSTATUS -> {backup_record['original_status']}")
                return True
            else:
                self.log_service.warning(f"恢复申办记录表记录 {backup_record['id']} 失败：无受影响的行")
                return False
                
        except Exception as e:
            self.log_service.error(f"恢复申办记录表状态失败: {str(e)}")
            return False
    
    def get_backup_summary(self) -> Dict[str, Any]:
        """获取备份记录摘要"""
        if not self.backup_records:
            return {'total': 0, 'restored': 0, 'pending': 0}
            
        total = len(self.backup_records)
        restored = len([r for r in self.backup_records if r.get('restored', False)])
        pending = total - restored
        
        return {
            'total': total,
            'restored': restored, 
            'pending': pending,
            'records': self.backup_records
        }
    
    def format_existing_records_message(self, existing_records: List[Dict]) -> str:
        """格式化现有记录信息为用户友好的消息"""
        if not existing_records:
            return "未发现重复申办记录"
            
        message_lines = [f"发现 {len(existing_records)} 条ETC相关记录：\n"]
        
        for i, record in enumerate(existing_records, 1):
            table_name = "货车用户" if record['table'] == 'hcb_truckuser' else "申办记录"
            status_desc = self._get_status_description(record)
            
            message_lines.append(
                f"{i}. 【{table_name}表】车牌：{record['car_num']} | "
                f"姓名：{record['name']} | 状态：{status_desc} | "
                f"匹配：{record['match_type']}"
            )
            
            if record.get('etc_sn'):
                message_lines.append(f"   ETC卡号：{record['etc_sn']}")
            if record.get('obu_no'):
                message_lines.append(f"   OBU号：{record['obu_no']}")
            message_lines.append("")
        
        message_lines.append("系统将临时修改这些记录的状态以允许重新申办，")
        message_lines.append("申办完成后会自动恢复原状态。")
        
        return "\n".join(message_lines)
    
    def _get_status_description(self, record: Dict) -> str:
        """获取状态描述"""
        if record['table'] == 'hcb_truckuser':
            status_map = {
                '0': '暂无ETC状态',
                '1': '正常', 
                '2': 'ETC黑名单',
                '3': '待激活',
                '4': '已注销'
            }
            return status_map.get(record['current_status'], f"未知状态({record['current_status']})")
        else:
            status_map = {
                '0': '未完成',
                '1': '已支付',
                '2': '初审中',
                '3': '待发行',
                '4': '发行中',
                '5': '配送中',
                '6': '已完成',
                '7': '已激活',
                '8': '已驳回',
                '10': '已注销',
                '11': '已发行'
            }
            return status_map.get(record['current_status'], f"未知状态({record['current_status']})")
    
    def _get_truckuser_status_description(self, status: str) -> str:
        """获取货车用户状态描述"""
        status_map = {
            '0': '暂无ETC状态',
            '1': '正常',
            '2': 'ETC黑名单',
            '3': '待激活',
            '4': '已注销'
        }
        return status_map.get(status, f'未知状态({status})')
    
    def _get_trucketcapply_status_description(self, status: str) -> str:
        """获取货车申办状态描述"""
        status_map = {
            '0': '未完成', '1': '已支付', '2': '初审中', '3': '待发行',
            '4': '发行中', '5': '配送中', '6': '已完成', '7': '已激活',
            '8': '已驳回', '10': '已注销', '11': '已发行'
        }
        return status_map.get(status, f'未知状态({status})')
    
    def filter_records_need_modify(self, existing_records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        过滤需要修改状态的记录 - 临时修改：所有记录都需要修改
        :param existing_records: 所有重复记录
        :return: (需要修改的记录列表, 跳过的记录列表)
        """
        records_to_modify = []
        records_to_skip = []
        
        # 🔥 临时修改：让所有记录都需要被修改，不进行状态过滤
        for record in existing_records:
            records_to_modify.append(record)
        
        self.log_service.info(f"过滤结果（临时修改-无状态过滤）：需要修改{len(records_to_modify)}条，跳过{len(records_to_skip)}条")
        
        return records_to_modify, records_to_skip 
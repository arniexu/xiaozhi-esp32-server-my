# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import sys
import json
import base64
import os
import tempfile
import uuid
import time
import urllib.parse
import oss2

from typing import List
from Tea.core import TeaCore

from alibabacloud_facebody20191230.client import Client as FacebodyClient
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_darabonba_env.client import Client as EnvClient
from alibabacloud_facebody20191230 import models as facebody_models
from alibabacloud_tea_console.client import Client as ConsoleClient
from alibabacloud_darabonba_string.client import Client as StringClient
from alibabacloud_tea_util.client import Client as UtilClient


# 人脸数据库配置
FACE_DB_NAME = "xiaozhi_faces"
FACE_DATA_FILE = "data/face_data.json"
FACEBODY_REGION = 'cn-shanghai'  # 人脸识别服务区域

# OSS配置
OSS_REGION = 'cn-shanghai'  # OSS存储区域（必须与人脸识别服务同区域）
OSS_BUCKET_NAME = 'faces-my-shanghai'  # 您的OSS bucket名称
OSS_ENDPOINT = f'https://oss-{OSS_REGION}.aliyuncs.com'

# OSS客户端实例
_oss_bucket = None


def _get_oss_bucket():
    """获取OSS bucket实例"""
    global _oss_bucket
    if _oss_bucket is None:
        try:
            # 获取访问密钥
            access_key_id = EnvClient.get_env('ALIBABA_CLOUD_ACCESS_KEY_ID')
            access_key_secret = EnvClient.get_env('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
            
            if not access_key_id or not access_key_secret:
                raise Exception("请设置 ALIBABA_CLOUD_ACCESS_KEY_ID 和 ALIBABA_CLOUD_ACCESS_KEY_SECRET 环境变量")
            
            # 初始化OSS
            auth = oss2.Auth(access_key_id, access_key_secret)
            _oss_bucket = oss2.Bucket(auth, OSS_ENDPOINT, OSS_BUCKET_NAME)
            
            ConsoleClient.log(f'✅ OSS初始化成功 (Bucket: {OSS_BUCKET_NAME})')
            
        except Exception as e:
            ConsoleClient.log(f'❌ OSS初始化失败: {str(e)}')
            ConsoleClient.log('💡 提示: 请先创建OSS bucket或检查配置')
            raise e
    
    return _oss_bucket


def _upload_image_to_oss(image_base64: str, filename: str) -> str:
    """
    上传图片到OSS
    @param image_base64: base64编码的图片数据
    @param filename: 文件名
    @return: OSS URL
    """
    try:
        # 获取OSS bucket
        bucket = _get_oss_bucket()
        
        # 解码base64图片
        image_data = base64.b64decode(image_base64)
        
        # 上传到OSS
        object_key = f"faces/{filename}"
        result = bucket.put_object(object_key, image_data)
        
        if result.status == 200:
            # 生成公开访问的OSS URL（需要bucket设置为公共读）
            oss_url = f"https://{OSS_BUCKET_NAME}.oss-cn-shanghai.aliyuncs.com/{object_key}"
            ConsoleClient.log(f'✅ 图片上传OSS成功: {oss_url}')
            return oss_url
        else:
            raise Exception(f"OSS上传失败，状态码: {result.status}")
            
    except Exception as e:
        ConsoleClient.log(f'❌ OSS上传失败: {str(e)}')
        raise e


class Sample:
    def __init__(self):
        pass

    @staticmethod
    def create_client(
        region_id: str,
    ) -> FacebodyClient:
        """
        使用AK&SK初始化账号Client
        @param create_client_request_body:
        @return: Facebody
        @throws Exception
        """
        config = open_api_models.Config()
        # 您的AccessKey ID
        config.access_key_id = EnvClient.get_env('ALIBABA_CLOUD_ACCESS_KEY_ID')
        # 您的AccessKey Secret
        config.access_key_secret = EnvClient.get_env('ALIBABA_CLOUD_ACCESS_KEY_SECRET')
        # 您的可用区ID
        config.region_id = region_id
        return FacebodyClient(config)

    @staticmethod
    def create_face_db(
        client: FacebodyClient,
        db_name: str,
    ) -> None:
        """
        创建人脸数据库
        @param db_name: 数据库名称
        @return: void
        @throws Exception
        """
        try:
            request_body = facebody_models.CreateFaceDbRequest()
            request_body.name = db_name
            client.create_face_db(request_body)
            ConsoleClient.log('--------------------创建人脸数据库成功--------------------')
        except Exception as err:
            ConsoleClient.log('create facebody db error')
            ConsoleClient.log(err.message)

    @staticmethod
    def add_face_entity(
        client: FacebodyClient,
        db_name: str,
        entity_id: str,
    ) -> None:
        """
        添加实体
        @param db_name: 数据库名称
        @param entity_id: 实体ID
        @return: void
        @throws Exception
        """
        try:
            request_body = facebody_models.AddFaceEntityRequest()
            request_body.db_name = db_name
            request_body.entity_id = entity_id
            client.add_face_entity(request_body)
            ConsoleClient.log('--------------------创建人脸样本成功--------------------')
        except Exception as err:
            ConsoleClient.log('add face entity error.')
            ConsoleClient.log(err.message)

    @staticmethod
    def add_face(
        client: FacebodyClient,
        db_name: str,
        entity_id: str,
        image_url: str,
    ) -> None:
        """
        添加人脸数据
        @param db_name: 数据库名称
        @param entity_id: 实体ID
        @param image_url: 人脸图片地址，必须是同Region的OSS的图片地址。人脸必须是正面无遮挡单人人脸。
        @return: void
        @throws Exception
        """
        try:
            request_body = facebody_models.AddFaceRequest()
            request_body.db_name = db_name
            request_body.entity_id = entity_id
            request_body.image_url = image_url
            client.add_face(request_body)
            ConsoleClient.log('--------------------创建人脸数据成功--------------------')
        except Exception as err:
            ConsoleClient.log('add face error.')
            ConsoleClient.log(err.message)

    @staticmethod
    def search_face(
        client: FacebodyClient,
        db_name: str,
        image_url: str,
        limit: int,
    ) -> facebody_models.SearchFaceResponse:
        """
        搜索人脸
        @param db_name: 数据库名称
        @param image_url: 图片URL地址。必须是同Region的OSS地址
        @param limit: 搜索结果数量限制
        @return: Facebody.SearchFaceResponse
        @throws Exception
        """
        try:
            request_body = facebody_models.SearchFaceRequest()
            request_body.db_name = db_name
            request_body.image_url = image_url
            request_body.limit = limit
            response = client.search_face(request_body)
            ConsoleClient.log('--------------------人脸搜索完成--------------------')
            return response
        except Exception as err:
            ConsoleClient.log('search face error.')
            ConsoleClient.log(err.message)
            raise err


def _get_face_data():
    """获取本地人脸数据"""
    try:
        os.makedirs(os.path.dirname(FACE_DATA_FILE), exist_ok=True)
        if os.path.exists(FACE_DATA_FILE):
            with open(FACE_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        ConsoleClient.log(f'读取本地人脸数据失败: {str(e)}')
        return {}


def _save_face_data(data):
    """保存本地人脸数据"""
    try:
        os.makedirs(os.path.dirname(FACE_DATA_FILE), exist_ok=True)
        with open(FACE_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        ConsoleClient.log(f'保存本地人脸数据失败: {str(e)}')


async def add_person(conn, name: str, image: str):
    """
    添加人员
    @param conn: 连接对象
    @param name: 人员姓名
    @param image: base64编码的图片数据
    """
    ConsoleClient.log(f'开始添加人员: {name}')
    try:
        # 创建Facebody客户端
        ConsoleClient.log(f'创建Facebody客户端，区域: {FACEBODY_REGION}')
        client = Sample.create_client(FACEBODY_REGION)
        
        # 生成唯一的entity_id
        entity_id = f"person_{uuid.uuid4().hex[:8]}"
        ConsoleClient.log(f'生成entity_id: {entity_id}')
        
        # 确保人脸数据库存在
        ConsoleClient.log(f'确保人脸数据库存在: {FACE_DB_NAME}')
        Sample.create_face_db(client, FACE_DB_NAME)
        
        # 创建人脸样本
        ConsoleClient.log(f'创建人脸样本，entity_id: {entity_id}')
        Sample.add_face_entity(client, FACE_DB_NAME, entity_id)
        
        try:
            # 上传图片到OSS (使用英文文件名避免编码问题)
            timestamp = int(time.time())
            # 使用英文文件名避免URL编码问题
            filename = f"person_{timestamp}_{entity_id}.jpg"
            ConsoleClient.log(f'🔄 上传图片到OSS: {filename}')
            
            oss_url = _upload_image_to_oss(image, filename)
            
            # 使用OSS URL调用阿里云人脸添加API
            ConsoleClient.log(f'🔄 使用OSS URL调用阿里云API添加人脸: {oss_url}')
            
            # 调用阿里云人脸添加API
            Sample.add_face(client, FACE_DB_NAME, entity_id, oss_url)
            
            # 保存人员信息到本地数据库
            ConsoleClient.log('读取现有人脸数据')
            face_data = _get_face_data()
            face_data[entity_id] = {
                "name": name,
                "entity_id": entity_id,
                "oss_url": oss_url,
                "filename": filename,
                "created_at": timestamp
            }
            ConsoleClient.log(f'保存人员信息到数据库: {name} -> {entity_id}')
            _save_face_data(face_data)
            
            ConsoleClient.log(f'✅ 成功添加人员 {name} 到阿里云人脸数据库')
            await conn.websocket.send(
                json.dumps({
                    "type": "face", 
                    "action": "add",
                    "status": "success", 
                    "message": f"成功添加人员: {name}",
                    "data": {
                        "name": name, 
                        "entity_id": entity_id,
                        "oss_url": oss_url,
                        "method": "alibaba_cloud_with_oss"
                    }
                })
            )
                
        except Exception as e:
            ConsoleClient.log(f'❌ 添加人员失败: {str(e)}')
            # 如果失败，仍然保存到本地数据库以便测试
            face_data = _get_face_data()
            face_data[entity_id] = {
                "name": name,
                "entity_id": entity_id,
                "created_at": time.time(),
                "error": str(e)
            }
            _save_face_data(face_data)
            raise e
                
    except Exception as e:
        ConsoleClient.log(f'添加人员失败: {str(e)}')
        await conn.websocket.send(
            json.dumps({
                "type": "face", 
                "action": "add",
                "status": "error", 
                "message": f"添加人员失败: {str(e)}"
            })
        )


async def find_person(conn, image: str):
    """
    查找人员
    @param conn: 连接对象
    @param image: base64编码的图片数据
    """
    ConsoleClient.log('开始查找人员')
    try:
        # 创建Facebody客户端
        ConsoleClient.log(f'创建Facebody客户端，区域: {FACEBODY_REGION}')
        client = Sample.create_client(FACEBODY_REGION)
        
        try:
            # 上传搜索图片到OSS
            timestamp = int(time.time())
            search_filename = f"search_{timestamp}_{uuid.uuid4().hex[:8]}.jpg"
            ConsoleClient.log(f'🔄 上传搜索图片到OSS: {search_filename}')
            
            search_oss_url = _upload_image_to_oss(image, search_filename)
            
            # 使用OSS URL调用阿里云人脸搜索API
            ConsoleClient.log(f'🔍 使用OSS URL调用阿里云人脸搜索API: {search_oss_url}')
            
            # 调用阿里云人脸搜索API
            response = Sample.search_face(
                client=client,
                db_name=FACE_DB_NAME,
                image_url=search_oss_url,
                limit=1  # 只返回最匹配的结果
            )
            
            if response and response.body and response.body.data:
                match_list = response.body.data.match_list
                
                if match_list and len(match_list) > 0:
                    # 获取最佳匹配
                    best_match = match_list[0]
                    
                    # 尝试从 face_items 获取匹配信息
                    entity_id = None
                    confidence = 0.0
                    
                    if hasattr(best_match, 'face_items') and best_match.face_items:
                        face_item = best_match.face_items[0]  # 获取第一个面部项
                        entity_id = getattr(face_item, 'entity_id', None)
                        confidence = getattr(face_item, 'score', 0.0)
                        ConsoleClient.log(f'🎯 从face_items找到匹配: entity_id={entity_id}, confidence={confidence}')
                    else:
                        # 尝试其他可能的属性名
                        entity_id = getattr(best_match, 'entity_id', None) or getattr(best_match, 'face_id', None) or getattr(best_match, 'id', None)
                        confidence = getattr(best_match, 'score', 0.0) or getattr(best_match, 'qualitie_score', 0.0)
                        ConsoleClient.log(f'🎯 从其他属性找到匹配: entity_id={entity_id}, confidence={confidence}')
                    
                    if entity_id:
                        # 从本地数据获取姓名
                        face_data = _get_face_data()
                    person_info = face_data.get(entity_id, {})
                    person_name = person_info.get('name', '未知')
                    
                    ConsoleClient.log(f'✅ 阿里云搜索成功，找到: {person_name} (entity_id: {entity_id}, 置信度: {confidence})')
                    
                    await conn.websocket.send(
                        json.dumps({
                            "type": "face", 
                            "action": "find",
                            "status": "success", 
                            "message": "找到匹配的人员",
                            "data": {
                                "name": person_name,
                                "entity_id": entity_id,
                                "confidence": confidence,
                                "search_method": "alibaba_cloud_with_oss"
                            }
                        })
                    )
                else:
                    ConsoleClient.log('❌ 阿里云搜索失败：未找到匹配的人员')
                    
                    await conn.websocket.send(
                        json.dumps({
                            "type": "face", 
                            "action": "find",
                            "status": "error", 
                            "message": "未找到匹配的人员",
                            "data": {
                                "search_method": "alibaba_cloud_with_oss"
                            }
                        })
                    )
            else:
                raise Exception(f"阿里云API返回错误: {response.body.message}")
                
            # 清理搜索图片（可选）
            try:
                bucket = _get_oss_bucket()
                bucket.delete_object(f"faces/{search_filename}")
                ConsoleClient.log(f'🗑️  清理搜索图片: {search_filename}')
            except:
                pass  # 清理失败不影响主要功能
                
        finally:
            # 不再需要清理临时文件
            pass
                
    except Exception as e:
        ConsoleClient.log(f'查找人员失败: {str(e)}')
        await conn.websocket.send(
            json.dumps({
                "type": "face", 
                "action": "find",
                "status": "error", 
                "message": f"查找人员失败: {str(e)}"
            })
        )


async def list_people(conn):
    """
    列出所有人员
    @param conn: 连接对象
    """
    ConsoleClient.log('开始列出所有人员')
    try:
        ConsoleClient.log('读取本地人脸数据')
        face_data = _get_face_data()
        
        people_list = []
        for entity_id, info in face_data.items():
            ConsoleClient.log(f'找到人员: {info.get("name", "未知")} (entity_id: {entity_id})')
            people_list.append({
                "name": info.get('name', '未知'),
                "entity_id": entity_id,
                "created_at": info.get('created_at', 0)
            })
        
        ConsoleClient.log(f'共找到 {len(people_list)} 个人员，准备发送响应')
        
        await conn.websocket.send(
            json.dumps({
                "type": "face", 
                "action": "list",
                "status": "success", 
                "message": f"共找到 {len(people_list)} 个人员",
                "data": {
                    "count": len(people_list),
                    "people": people_list
                }
            })
        )
        
        ConsoleClient.log('成功发送人员列表响应')
        
    except Exception as e:
        ConsoleClient.log(f'列出人员失败: {str(e)}')
        await conn.websocket.send(
            json.dumps({
                "type": "face", 
                "action": "list",
                "status": "error", 
                "message": f"列出人员失败: {str(e)}"
            })
        )

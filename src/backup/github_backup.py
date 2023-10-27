"""
    Created by howie.hu at 2022-01-15.
    Description: 基于github做备份
        - 命令：PIPENV_DOTENV_LOCATION=./pro.env pipenv run python src/backup/github_backup.py
    Changelog: all notable changes to this file will be documented
"""

from github import Github, GithubException

from src.backup.base import BackupBase
from src.config import Config
from src.utils import LOGGER
from src.backup.utils import GitHubRepo


class GithubBackup(BackupBase):
    """基于Github进行文章备份"""

    def __init__(self, init_config: dict):
        """
        初始化相关变量
        :param init_config:
        """
        super().__init__(backup_type="github", init_config=init_config or {})
        github_token = init_config.get("github_token", Config.LL_GITHUB_TOKEN)
        github_repo = init_config.get("github_repo", Config.LL_GITHUB_REPO)
        self.repo = GitHubRepo(token=github_token, repo=github_repo, base_url=Config.LL_GITHUB_BASE_URL)
        # 是否每次更新都强制备份，默认只备份一次
        self.force_backup = init_config.get("force_backup", False)

    def save(self, backup_data: dict) -> bool:
        """执行备份动作

        Args:
            backup_data (dict): 备份数据

        Returns:
            bool: 是否成功
        """
        # 以下字段必须存在
        doc_source = backup_data["doc_source"]
        doc_source_name = backup_data["doc_source_name"]
        doc_name = backup_data["doc_name"]
        # 源文件
        doc_html = backup_data["doc_html"]

        path_in_repo = Config.LL_GITHUB_BACKUP_PATH_IN_REPO.format_map(
            {
                "doc_source": doc_source,
                "doc_source_name": doc_source_name,
                "doc_name": doc_name,
            }
        )
        is_backup = self.is_backup(
            doc_source=doc_source,
            doc_source_name=doc_source_name,
            doc_name=doc_name,
        )

        # 在数据库存在就默认线上必定存在，希望用户不操作这个仓库造成状态不同步
        if not is_backup or self.force_backup:
            # 上传前做是否存在检测，没有备份过继续远程备份
            # 已存在的但是数据库没有状态需要重新同步
            try:
                # 先判断文件是否存在
                try:
                    # 存在就更新
                    self.repo.update_file(
                        path_in_repo, doc_html, f"Update {path_in_repo}"
                    )
                except Exception as _:
                    # 不存在就上传
                    self.repo.create_file(path_in_repo, doc_html, f"Add {path_in_repo}")

                LOGGER.info(f"Backup({self.backup_type}): {path_in_repo} 备份成功！")
                # 保存当前文章状态
                self.save_backup(
                    doc_source=doc_source,
                    doc_source_name=doc_source_name,
                    doc_name=doc_name,
                )
            except GithubException as e:
                LOGGER.error(f"Backup({self.backup_type}): {path_in_repo} 备份失败！{e}")
        else:
            LOGGER.info(f"Backup({self.backup_type}): {path_in_repo} 已存在！")

    def delete(self, doc_source: str, doc_source_name: str, doc_name: str) -> bool:
        """删除某个文件

        Args:
            doc_source (str): 文章获取源
            doc_source_name (str): 文章源
            doc_name (str): 文章名字
        Returns:
            bool: 是否成功
        """
        file_path = f"{doc_source}/{doc_source_name}/{doc_name}.html"
        op_res = True
        try:
            _ = self.repo.delete_file(
                file_path, f"Remove {file_path}"
            )
            LOGGER.info(f"Backup({self.backup_type}): {file_path} 删除成功！")
            # 删除当前文章状态
            self.delete_backup(
                doc_source=doc_source,
                doc_source_name=doc_source_name,
                doc_name=doc_name,
            )
        except Exception as e:
            op_res = False
            LOGGER.error(f"Backup({self.backup_type}): {file_path} 删除失败！{e}")
        return op_res


if __name__ == "__main__":
    test_backup_data = {
        "doc_id": "test",
        "doc_source": "liuli_wechat",
        "doc_source_name": "老胡的储物柜",
        "doc_name": "打造一个干净且个性化的公众号阅读环境_test",
        "doc_link": "https://mp.weixin.qq.com/s/NKnTiLixjB9h8fSd7Gq8lw",
        "doc_html": "Hello world2",
    }
    github_backup = GithubBackup({"force_backup": False})
    github_backup.save(test_backup_data)
    # github_backup.delete(
    #     doc_source="liuli_book",
    #     doc_source_name="老胡的储物柜",
    #     doc_name="打造一个干净且个性化的公众号阅读环境",
    # )

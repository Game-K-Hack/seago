import os
import re
import yaml

DATASET = "C:/Users/Game_K/Desktop"

def is_correct_directory(path:str) -> bool:
    return os.path.isdir(path) and re.match("[-a-z]{1,}", path.split("/")[-1])

def is_yaml_file(path:str) -> bool:
    return os.path.isfile(path) and re.match("[-a-z]{1,}\\.(yaml|yml)", path.split("/")[-1])

def get_environments() -> dict:
    groups = {
        "k8s-core-staging-deployment": {}
    }
    for group in groups.keys():
        current_group_path = DATASET + "/" + group
        for envpath in os.listdir(current_group_path):
            current_env_path = current_group_path + "/" + envpath
            if is_correct_directory(current_env_path):
                groups[group][envpath] = {}
                for namespace in os.listdir(current_env_path):
                    current_namespace_path = current_env_path + "/" + namespace
                    if is_correct_directory(current_namespace_path):
                        groups[group][envpath][namespace] = {}
                        for project in os.listdir(current_namespace_path):
                            current_project_path = current_namespace_path + "/" + project
                            if is_correct_directory(current_project_path):
                                groups[group][envpath][namespace][project] = {}
                                for filename in os.listdir(current_project_path):
                                    current_filename_path = current_project_path + "/" + filename
                                    if is_yaml_file(current_filename_path):
                                        data = [i for i in yaml.load_all(open(current_filename_path), Loader=yaml.FullLoader)]
                                        if len(data) > 0 and "kind" in data[0].keys() and data[0]["kind"] == "SealedSecret":
                                            groups[group][envpath][namespace][project]["Path"] = current_filename_path
                                            groups[group][envpath][namespace][project]["Group"] = group
                                            groups[group][envpath][namespace][project]["SealedSecret"] = {
                                                (conf["metadata"]["name"]
                                                    if "metadata" in conf and "name" in conf["metadata"] else (
                                                        conf["spec"]["template"]["metadata"]["name"]
                                                            if "spec" in conf and 
                                                            "template" in conf["spec"] and 
                                                            "metadata" in conf["spec"]["template"] and 
                                                            "name" in conf["spec"]["template"]["metadata"] 
                                                            else ""
                                                    )
                                                ):conf["spec"]["encryptedData"]
                                                for conf in data
                                            }
                                            groups[group][envpath][namespace][project]["Data"] = data

    environments = {}

    for g in groups.keys():
        for e in groups[g].keys():
            environments[e] = groups[g][e]
    
    return environments
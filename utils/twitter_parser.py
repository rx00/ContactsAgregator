def user_extractor(friends_json):
    user_list = friends_json["users"]
    cooked_users = {}
    for user in user_list:
        current_id = user["id_str"]
        current_user_dict = {
            "current_name": user["name"],
            "current_domain": user["screen_name"],
            "current_mined_vk": None
        }
        if "url" in user["entities"]:
            link_dump = user["entities"]["url"]["urls"][0]["display_url"]
            link_parts = link_dump.split('/')
            if len(link_parts) > 1:
                if "vk.com" in link_parts[0]:
                    current_user_dict["current_mined_vk"] = link_parts[1]
                    cooked_users[current_id] = current_user_dict

    return cooked_users

# https://twitter.com/intent/user?user_id=xxx

import pandas as pd

import adder


def getStanceByEndorse(endorse):
    if endorse <= 3:
        return "FAVOR"
    elif endorse >= 5:
        return "AGAINST"
    else:
        return "NONE"

def addOrganizationInfo(key, val, dic):
    try:
        for i,d in enumerate(val):
            key_string_city = "Organization_city" + str(i)
            key_string_country = "Organization_country" + str(i)
            key_string_street = "Organization_street" + str(i)
            key_string_organization = "Organization_org" + str(i)
            try:
                dic[key_string_city] = d['address_spec']['city']
                dic[key_string_country] = d['address_spec']['country']
                dic[key_string_street] = d['address_spec']['street']
                dic[key_string_organization] = d['address_spec']['organizations']['organization']
            except KeyError:
                print "Key Error (wrong path) while storing organization address spec"
            except:
                print "Something went wrong storing organization address spec"

        dic["Num_of_organizations"] = len(val)
        return dic
    except:
        key_string_city = "Organization_city0"
        key_string_country = "Organization_country0"
        key_string_street = "Organization_street0"
        key_string_organization = "Organization_org0"
        try:
            dic[key_string_city] = val['address_spec']['city']
            dic[key_string_country] = val['address_spec']['country']
            dic[key_string_street] = d['address_spec']['street']
            dic[key_string_organization] = d['address_spec']['organizations']['organization']
            dic["Num_of_organizations"] = 1
        except KeyError:
            print "Key Error (wrong path) while storing organization address spec"
        except:
            print "Something went wrong storing organization address spec"
    return dic

def addAuthorInfo(key,val, dic):
    try:
        for i,d in enumerate(val):
            key_string_author = "Author_name" + str(i)
            try:
                dic[key_string_author] = d['wos_standard']
            except KeyError:
                print "Key Error (wrong path) while storing organization address spec"
            except:
                print "Something went wrong storing organization address spec"
        dic["Num_of_authors"] = len(val)
        return dic
    except:
        key_string_author = "Author_name0"
        try:
            dic[key_string_author] = dic['wos_standard']
            dic["Num_of_authors"] = 1
            return dic
        except KeyError:
            print "Key Error (wrong path) while storing organization address spec"
        except:
            print "Something went wrong storing organization address spec"
        return dic

tcp_data = pd.read_csv("../../tcp_abstracts.txt")
def getImportantInfo(dic, index):
    # Create an empty new dictionary
    new_dic = {}
    # Add fields from TCP
    new_dic["_id"] = tcp_data.Id.iloc[index]
    new_dic["Abstract"] = tcp_data.Abstract.iloc[index].replace("|",",")
    new_dic["Endorsement"] = tcp_data.Endorse.iloc[index]
    new_dic["Stance"] = getStanceByEndorse(tcp_data.Endorse.iloc[index])
    new_dic["Year"] = tcp_data.Year.iloc[index]
    new_dic["Category"] = tcp_data.Cat.iloc[index]
    new_dic["Title"] = tcp_data.Title.iloc[index].replace("|",",")

    # Add new data from WoS
    new_dic = adder.add(dic, new_dic)

    return new_dic

def addToDict(key, val, dic, counter):
    # Debugging purposes..
    print 30*"=" + " LEAF VALUE " + 30*"="
    print
    print "Key: " + key
    print "Value: " + str(val)
    print

    # No information in count values
    if key=='count':
        return dic, counter
    # The key 'address_name' is usually a list, store properly by using the method..
    if key == 'address_name':
        dic = addOrganizationInfo(key, val, dic)
    # The key 'name' is usually a list of authors, store properly by using the method
    elif key == 'name':
        dic = addAuthorInfo(key, val, dic)
    # See if the dictionary with the key is taken, if yes add a number behind the new key
    # otherwise store the key in dictionary with proper value
    try:
        if dic[key]:
            counter += 1
            new_key = key + str(counter)
            "Key already used.. Counter now = " + str(counter)
            dic[new_key] = val
    # No key found, store the key-value pair
    except KeyError:
        dic[key] = val
    except:
        print("Some other than KeyError appeared when adding key-value to dictionary")
    # Return the dictionary and counter..
    return dic, counter


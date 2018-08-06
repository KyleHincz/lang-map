
# -*- coding: utf-8 -*-
"""
This function translates an English word and displays a map of Europe with its respective translations. Each country is color coded based on how similar the word is between different languages.

Created on Sun Jul 29 21:22:54 2018

@author: khincz
"""


from bokeh.io import show, output_notebook
from bokeh.palettes import Viridis6 as palette
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, LabelSet, LogColorMapper
from bokeh.palettes import Viridis256 as palette
output_notebook()

import googletrans
from transliterate import translit
import collections # For kph
import re  # For kph
import pandas as pd # for createDataFrame
import ast # for transforming coordinates
#from numpy import nan

def trans_late_literate(input_word):
    translator = googletrans.Translator()

    for language in language_list:
    
        if language in ('bg', 'el', 'hy', 'ka', 'l1', 'mk', 'mn', 'ru', 'sr', 'uk'):
          result = translator.translate(word,dest=language,src='en').text.lower()
          result_transliterated = translit(result, language, reversed=True)
          d[language]=result_transliterated
          d[language+'.t']=result

        elif language == 'be':
          result = translator.translate(word,dest=language,src='en').text.lower()
          result_transliterated = translit(result, 'ru', reversed=True)
          result_transliterated = result_transliterated.replace('ў' , 'u')
          d[language]=result_transliterated
          d[language+'.t']=result
      
        else:        
          result = translator.translate(word,dest=language,src='en').text.lower()
          d[language]=result    
  
def kph_encode(inputstring):  # type: (str) -> str
  """
 This function  uses the 'Koelner Phonetik' module # Copyright (C) 2008-2017 Robert Schindler (GPL).
 Function adapted for non-german characters.
  
 Examples of usage:
  >>> kph_encode("Moritz Müller")
  '678657'

  kph_encode(string inputstring) -> string
   Returns the phonetic code of given inputstring.
  """
  
  RULES = collections.OrderedDict()          
  #RULES[re.compile(r".[AEIJOUYÄÖÜÀÁÂÃÄÅÆÈÉÊËÌÍÎÏÒÓÔÕÖØÙÚÛÜÝĀĂĄĪĮİĒĘĚŐŪŮŰŲỲŶŸĦḤI].", re.I)]    = "0"
  RULES[re.compile(r".[B].", re.I)]                   	= "1"
  RULES[re.compile(r".[P][^H]", re.I)]                	= "1"
  RULES[re.compile(r".[DT][^CSZ]", re.I)]            		= "2"
  RULES[re.compile(r".[DTĎĐŤȚ]", re.I)]               		= "2"
  RULES[re.compile(r".[FVWẀẂẄŴ].", re.I)]             	= "3"
  RULES[re.compile(r".[P][H]", re.I)]                 	= "3"
  RULES[re.compile(r".[GKQĞĠĢ].", re.I)]              		= "4"
  RULES[re.compile(r"\s[C][AÀÁÂHKLOQRUX]", re.I)]       	= "4"
  RULES[re.compile(r"[^SZ][C][AHKOQUX]", re.I)]       		= "4"
  RULES[re.compile(r"[ÇĆĊČ]", re.I)]             		= "4"
  RULES[re.compile(r"[^CKQ][X].", re.I)]              	= "48"
  RULES[re.compile(r".[LĹĻĽŁḶL].", re.I)]             		= "5"
  RULES[re.compile(r".[MNÑŃŅŇ].", re.I)]              	= "6"
  RULES[re.compile(r".[RŔŘ].", re.I)]                 		= "7"
  RULES[re.compile(r".[ṢȘŚŞŠSZßŹŻŽ].", re.I)]           = "8"
  RULES[re.compile(r"[SZ][C].", re.I)]                	= "8"
  RULES[re.compile(r"\s[C][^AÀÁÂHKLOQRUX]", re.I)]      = "8"
  RULES[re.compile(r"[C][^AHKOQUX]", re.I)]           	= "8"
  RULES[re.compile(r".[DT][CSZ]", re.I)]              	= "8"
  RULES[re.compile(r"[CKQĶ][X].", re.I)]              	= "8"
  RULES[re.compile(r"[CKQĶ].", re.I)]                 	= "8"
  
  INVALID_CHAR_PATTERN = re.compile(r"[^a-zäöüßILÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÑÒÓÔÕÖØÙÚÛÜÝĀĂĄĆĊČĎĐĒĘĚĞĠĢĦĪĮİĶĹĻĽŁŃŅŇŐŔŘŚŞŠŤŪŮŰŲŴŶŸŹŻŽȘȚḤḶṢẀẂẄỲ\s]", re.I) 

  # remove anything except characters and whitespace
  inputstring = INVALID_CHAR_PATTERN.sub("", inputstring)

  encoded = ""
  for i in range(len(inputstring)):
      part = inputstring[i-1 : i+2]
      if len(inputstring) == 1:
          part = " %s " % inputstring[0]
      elif i == 0:
          part = " %s" % inputstring[:2]
      elif i == len(inputstring) - 1:
          part = "%s " % inputstring[i - 1:]

      for rule, code in RULES.items():
          if rule.match(part):
              encoded += code
              break

  # remove immediately repeated occurrences of phonetic codes
  while [v for v in RULES.values() if encoded.find(v*2) != -1]:
      for v in RULES.values():
          encoded = encoded.replace(v*2, v)

  if encoded:
      encoded = encoded[0] + encoded[1:].replace("0", "")

  return encoded


def cluster(kph_list):
  '''Arrange data into groups where successive elements differ by no more than *maxgap*

      >>> cluster([1, 6, 9, 100, 102, 105, 109, 134, 139]) maxgap=10
      [[1, 6, 9], [100, 102, 105, 109], [134, 139]]

      >>> cluster([1, 6, 9, 99, 100, 102, 105, 134, 139, 141]) maxgap=10
      [[1, 6, 9], [99, 100, 102, 105], [134, 139, 141]]

  '''

  maxgap = 0.05 # controls 
  kph_list.sort()
  groups = [[kph_list[0]]]
  for x in kph_list[1:]:
      if abs(x - groups[-1][-1]) <= maxgap:
          groups[-1].append(x)
      else:
          groups.append([x])
  not_linked = []     
  linked =[]
  
  for i in groups:
      if len(i) ==1:
          not_linked.append(i[0])
      else: 
          linked.append(i)
  return linked



def assign_group(target,lst):
  for i,lst in enumerate(lst):
      for j,color in enumerate(lst):
          if color == target:
              return (i)
       
  return (None)


# sample words
d_master = {'monitor':{'en': ('monitor', 6.27), 'sq': ('monitor', 6.27), 'ca': ('monitor', 6.27), 'be': ('manіtor', 6.27), 'be.t': ('манітор', 6.27), 'bs': ('monitor', 6.27), 'bg': ('monitor', 6.27), 'bg.t': ('монитор', 6.27), 'hr': ('monitor', 6.27), 'cs': ('monitor', 6.27), 'da': ('overvåge', 3.734), 'et': ('ekraan', 4.76), 'fi': ('monitori', 6.27), 'fr': ('moniteur', 6.27), 'de': ('monitor', 6.27), 'el': ('othoni', 2.6), 'el.t': ('οθόνη', 2.6), 'hu': ('monitor', 6.27), 'is': ('fylgjast með', 3.54826), 'ga': ('monatóireacht a dhéanamh', 6.274826), 'it': ('tenere sotto controllo', 2.6782486275), 'lv': ('monitors', 6.278), 'lt': ('stebėti', 8.212), 'lb': ('iwwerwaachen', 3.73486), 'mk': ('sledi', 8.52), 'mk.t': ('следи', 8.52), 'mt': ('timmonitorja', 2.627), 'nl': ('monitor', 6.27), 'no': ('følge', 3.54), 'pl': ('monitor', 6.27), 'pt': ('monitor', 6.27), 'ro': ('monitor', 6.27), 'ru': ('monitor', 6.27), 'ru.t': ('монитор', 6.27), 'sr': ('monitor', 6.27), 'sr.t': ('монитор', 6.27), 'sk': ('monitor', 6.27), 'sl': ('monitor', 6.27), 'es': ('monitor', 6.27), 'sv': ('övervaka', 3.7348), 'tr': ('izlemek', 8.564), 'uk': ('monitor', 6.27), 'uk.t': ('монітор', 6.27), 'la': ('monitor', 6.27), 'cy': ('monitro', 6.27), 'eu': ('monitore', 6.27), 'gl': ('monitor', 6.27)}} 
  

# input control
word = input("Enter English word to translate:") 
word = re.sub(r"\s*[^A-Za-z]+\s*", " ", word)
if len(word.split()) > 2:
  print("Maximum 2 words per translation")
  word = input("Enter English word to translate") 
  word = re.sub(r"\s*[^A-Za-z]+\s*", " ", word)
elif len(word) > 20 or len(word) == 0:
   print("Input needs to be between 1 and 20 characters long")
   word = input("Enter English word to translate") 
   word = re.sub(r"\s*[^A-Za-z]+\s*", " ", word)

# fetch google transaltions for word in all languages and transliterate to latin alphabet
d={}
language_list = ('en','sq','ca','be','bs','bg','hr','cs','da','et','fi','fr','de','el','hu','is','ga','it','lv','lt','lb','mk','mt','nl','no','pl','pt','ro','ru','sr','sk','sl','es','sv','tr','uk','la','cy','eu','gl')
d_detail = {}

if word not in d_master:
    trans_late_literate(word)
else:
    for entry in d_master[word]:
        d[entry] = d_master[word][entry][0] 

# calculate modified Koelner Phonetik Score for each translation and save in dictionary
for lang_key in language_list:
    encoded = kph_encode(d[lang_key])
    len_encoded = len(encoded)
    if encoded == 0 or encoded == '':
        d_detail[lang_key] = (d[lang_key],0.0)
    else:
        d_detail[lang_key] = (d[lang_key],int(encoded)/10**(len_encoded-1))

    if lang_key in ('be', 'bg', 'el', 'hy', 'ka', 'l1', 'mk', 'mn', 'ru', 'sr', 'uk'):
        if encoded == 0 or encoded == '':
            d_detail[lang_key+'.t'] = (d[lang_key+'.t'],0.0)
        else:
            d_detail[lang_key+'.t'] = (d[lang_key+'.t'],int(encoded)/10**(len_encoded-1))
      
d_master[word]= d_detail

d_country_langcode = {'Albania': 'sq', 'Austria': 'de', 'Belgium': 'nl', 'Bulgaria': 'bg', 'Bosnia and Herz.': 'bs', 'Belarus': 'be', 'Switzerland': 'de', 'Czech Rep.': 'cs', 'Germany': 'de', 'Denmark': 'da', 'Spain': 'es', 'Estonia': 'et', 'Finland': 'fi', 'France': 'fr', 'United Kingdom': 'en', 'Greece': 'el', 'Croatia': 'hr', 'Hungary': 'hu', 'Ireland': 'ga', 'Iceland': 'is', 'Italy': 'it', 'Lithuania': 'lt', 'Luxembourg': 'lb', 'Latvia': 'lv', 'Macedonia': 'mk', 'Netherlands': 'nl', 'Norway': 'no', 'Poland': 'pl', 'Portugal': 'pt', 'Romania': 'ro', 'Russia': 'ru', 'Serbia': 'sr', 'Slovakia': 'sk', 'Slovenia': 'sl', 'Sweden': 'sv', 'Turkey': 'tr', 'Ukraine': 'uk', 'Catalonia': 'ca', 'Malta': 'mt', 'Vatican City': 'la', 'Wales': 'cy', 'Basque Country': 'eu', 'Galicia': 'gl','Kosovo': 'sq', 'Moldova': 'ro', 'Montenegro': 'sr'}
d_langcode_language = {'sq': 'Albanian', 'de': 'German', 'nl': 'Dutch', 'bg': 'Bulgarian', 'bs': 'Bosnian', 'be': 'Belarusian', 'cs': 'Czech', 'da': 'Danish', 'es': 'Spanish', 'et': 'Estonian', 'fi': 'Finnish', 'fr': 'French', 'en': 'English', 'el': 'Greek', 'hr': 'Croatian', 'hu': 'Hungarian', 'ga': 'Irish', 'is': 'Icelandic', 'it': 'Italian', 'lt': 'Lithuanian', 'lb': 'Luxembourgish', 'lv': 'Latvian', 'mk': 'Macedonian', 'no': 'Norwegian', 'pl': 'Polish', 'pt': 'Portuguese', 'ro': 'Romanian', 'ru': 'Russian', 'sr': 'Serbian', 'sk': 'Slovak', 'sl': 'Slovenian', 'sv': 'Swedish', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ca': 'Catalan', 'mt': 'Maltese', 'la': 'Latin', 'cy': 'Welsh', 'eu': 'Basque', 'gl': 'Galician'}

# create dataframe that contains country, lang, translation and kph scores
df = pd.DataFrame.from_dict(data=d_master[word],orient='index').reset_index()
df['language']= df['index'].map(d_langcode_language)
df.rename( columns={"index": "LangCode", 0: "Translation", 1:"KPhscore", 'language':'Language'}, inplace=True)
df_countries = pd.DataFrame.from_dict(d_country_langcode,orient='index').reset_index()
df_countries.rename( columns={"index": "Country", 0: "LangCode"}, inplace=True)
final_df = pd.merge(df_countries,df,how='inner',on=['LangCode']).sort_values(by='KPhscore')

# cluster  words based on kph score and assign to numeric groups for display in bokeh
cluster_list = cluster(final_df['KPhscore'].tolist()) 
final_df['ScoreGroup'] = final_df['KPhscore'].apply(lambda z: assign_group(z, cluster_list))

# import coordinates file
df_csv = pd.read_csv("country_coordinates.csv",delimiter=';')

# turn coordinates into a list used by bokeh to draw map
df_csv['x'] = df_csv['x'].apply(lambda item: list(ast.literal_eval(item)))
df_csv['y'] = df_csv['y'].apply(lambda item: list(ast.literal_eval(item)))

#merge translated dictionary dataframe with coordinates
bokeh_df = pd.merge (df_csv, final_df, how='inner',on=['Country'])

#bokeh display settings
title = ("The word ''"+ bokeh_df['Translation'][bokeh_df['LangCode']=='en'].values[0]+ "'' in European languages")
source = ColumnDataSource(bokeh_df)
color_mapper = LogColorMapper(palette=palette)

p = figure(title=title, 
           x_range=(-25,43), y_range=(33,72),
           plot_width=950,plot_height=740,
            tooltips=[
        ("Country", "@Country"), ("Language", "@Language"), ("Similarity Score", "@KPhscore"), ("Similarity Group", "@ScoreGroup")
    ])
    
p.grid.grid_line_color = None
p.hover.point_policy = "follow_mouse"
p.patches('x', 'y', fill_alpha=0.4,
          fill_color={'field': 'ScoreGroup', 'transform': color_mapper},
                    line_color='white', line_width=1, source=source, hover_fill_alpha=0.4, hover_line_color = "#95c8d8", hover_fill_color = 'white')

labels = LabelSet(x = 'xc', y = 'yc', x_offset=-30, y_offset=-10,
                  text='Translation', text_color = 'black', text_font = 'Arial',
                  source=source)
p.add_layout(labels)

p.background_fill_color = "#95c8d8"
p.background_fill_alpha = 0.2
show(p)
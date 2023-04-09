import pandas as pd
from datetime import datetime
import regex as re
from case_scraper.scraper import collect_HTML_tables, extract_cases, extract_case_information
from case_scraper.extractor import find_president, unpackColumnDict
from case_scraper.pdf_functions import get_document_date

if __name__ == '__main__':
    import pandas as pd

    rows = collectHTMLTables("mergers")
    casesList = extractCases(rows)

    for caseDict in casesList:
        caseLink = caseDict["link"]
        caseInfo = extractCaseInformation(caseLink)
        caseDict.update(caseInfo)

        caseDict["Filed and Settled Same Day"] = "N/A"
        caseDict["Time from Complaint to Judgment"] = "N/A"
        caseDict["Dismissed?"] = "N/A"
        caseDict["Sitting President"] = "N/A"
        date_string = caseDict["caseDate"]
        date_object = datetime.datetime.strptime(date_string, '%B %d, %Y')
        president = find_president(date_object)
        caseDict["Sitting President"] = president
        caseDict["agency"] = "DOJ"
        if caseDict["openDateTime"] and caseDict["documents"]:
            # Deduplicate and sort the documents by date
            caseDict["documents"] = sorted({d["docLink"]: d for d in caseDict["documents"]}.values(),
                                           key=lambda k: k.get('docDateObj', datetime.datetime(1900, 1, 1)))

            regex_dict = {'complaint': re.compile(r'(?=.*complaint)', flags=re.I),
                          'motion': re.compile(r'(?=.*motion)', flags=re.I),
                          'judgement': re.compile(r'(?=.*judgement|.*judgment|.*opinion)', flags=re.I),
                          'expert': re.compile(r'(?=.*testimony|.*expert|.*comment|opposition|oral communications)',
                                               flags=re.I),
                          'dismiss': re.compile(r'(?=.*notice|.*stipulation|.*order)(?=.*dismiss)', flags=re.I),
                          'settlement': re.compile(r's(?=.*settlement|consent)', flags=re.I)}

            complaint = [doc for doc in caseDict["documents"] if
                         regex_dict['complaint'].search(doc["docTitle"].lstrip()) and not regex_dict['motion'].search(
                             doc["docTitle"].lstrip())]
            complaint = sorted(complaint, key=lambda k: k.get('docDateObj', datetime.datetime(1900, 1, 1)),
                               reverse=False)

            judgment = [doc for doc in caseDict["documents"] if
                        regex_dict['judgement'].search(doc["docTitle"].lstrip()) and not regex_dict['expert'].search(
                            doc["docTitle"].lstrip())]
            judgment = sorted(judgment, key=lambda k: k.get('docDateObj', datetime.datetime(1900, 1, 1)), reverse=False)

            dismiss = [doc for doc in caseDict["documents"] if regex_dict['dismiss'].search(doc["docTitle"])]
            dismiss = sorted(dismiss, key=lambda k: k.get('docDateObj', datetime.datetime(1900, 1, 1)), reverse=False)

            settlement = [doc for doc in caseDict["documents"] if regex_dict['settlement'].search(doc["docTitle"])]
            settlement = sorted(settlement, key=lambda k: k.get('docDateObj', datetime.datetime(1900, 1, 1)),
                                reverse=False)

            keyDocs = complaint + judgment + dismiss + settlement
            keyDocs = sorted(keyDocs, key=lambda k: k.get('docDateObj', datetime.datetime(1900, 1, 1)), reverse=False)
            caseDict["Key Documents Data"] = "N/A"
            caseDict["Key Documents Data"] = keyDocs

            # Count days from start to finish

            if complaint and judgment:
                complaintDate = complaint[0]["docDateObj"]
                judgmentDate = judgment[0]["docDateObj"]
                caseDict["Dismissed?"] = "No"
                if judgmentDate < complaintDate:
                    caseDict["Filed and Settled Same Day"] = "Likely Typo in Judgment Date"
                elif complaintDate == judgmentDate:
                    caseDict["Filed and Settled Same Day"] = "Yes"
                elif (judgmentDate - complaintDate).days <= 7:
                    caseDict["Filed and Settled Same Day"] = "Yes"
                else:
                    caseDict["Filed and Settled Same Day"] = "No"
                timeDiff = judgmentDate - complaintDate
                caseDict["Days from Complaint to Judgment/Dismissal"] = timeDiff.days
            elif complaint and dismiss:
                complaintDate = complaint[0]["docDateObj"]
                judgmentDate = dismiss[0]["docDateObj"]
                caseDict["Dismissed?"] = "Yes"
                timeDiff = judgmentDate - complaintDate
                if timeDiff.days <= 7:
                    caseDict["Filed and Settled Same Day"] = "Yes"
                caseDict["Days from Complaint to Judgment/Dismissal"] = timeDiff.days

    col_rename_dict = {"title": "Case Name",
                       "docketNo": "Docket No.",
                       "court": "Court",
                       "agency": "Enforcement Agency",
                       "caseType": "Case Type",
                       "openDate": "Case Open Date",
                       "Sitting President": "Sitting President",
                       "Filed and Settled Same Day": "Filed and Settled Same Day",
                       "Days from Complaint to Judgment/Dismissal": "Days from Complaint to Judgment/Dismissal",
                       "Dismissed?": "Dismissed?",
                       "violations": "Violations",
                       "market": "Market(s)",
                       "industry": "Industry(ies)",
                       'documents': "Documents",
                       'Key Documents Data': "Key Documents Data",
                       "link": "Case Link"}

    # create dataframe with columns from col_rename_dict.keys()
    df = pd.DataFrame(casesList, columns=col_rename_dict.keys())

    # rename the columns
    df.rename(columns=col_rename_dict, inplace=True)

    # unpack the 'documents' and 'Key Documents Data' columns
    df['Documents'] = df['Documents'].apply(unpackColumnDict)
    df["Key Documents Data"] = df["Key Documents Data"].apply(unpackColumnDict)

    # create a dictionary with all the key documents
    key_docs = {}
    for case in casesList:
        for doc in case["Key Documents Data"]:
            key_docs[doc["docTitle"]] = doc

    # replace the key documents in the dataframe with the dictionary items
    # df["Key Documents Data"] = df["Key Documents Data"].apply(lambda x: [key_docs[doc["docTitle"]] for doc in x])
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    # create the excel writer and sheet
    writer = pd.ExcelWriter("DOJ Tracker - Merger Cases.xlsx", engine='xlsxwriter')

    # create a sheet with only the unlitigated enforcement actions
    unlitigatedEnforcementActions = df[df["Filed and Settled Same Day"] == "Yes"]
    unlitigatedEnforcementActions.rename(columns={"Case Open Date": "Date Complaint/Settlement Filed"}, inplace=True)
    # write the dataframe to excel
    df.to_excel(writer, index=False, sheet_name="All Enforcement Actions")
    unlitigatedEnforcementActions.to_excel(writer, index=False, sheet_name="Unlitigated Enforcement Actions")

    workbook = writer.book
    allEnforcementActionsWorksheet = writer.sheets["All Enforcement Actions"]
    unlitigatedEnforcementActionsWorksheet = writer.sheets["Unlitigated Enforcement Actions"]
    # Add text wrapping and reduce height of cells
    # allEnforcementActionsWorksheet.set_text_wrap()
    allEnforcementActionsWorksheet.set_default_row(50)
    # unlitigatedEnforcementActionsWorksheet.set_text_wrapWa()
    unlitigatedEnforcementActionsWorksheet.set_default_row(50)

    # Adjust Column Widths
    allEnforcementActionsWorksheet.set_column('A:P', 100, None)
    unlitigatedEnforcementActionsWorksheet.set_column('A:P', 100, None)

    # Add text wrapping to the header row
    header_fmt = workbook.add_format({'bold': True, 'text_wrap': True, 'valign': 'top'})
    allEnforcementActionsWorksheet.set_row(0, None, header_fmt)
    unlitigatedEnforcementActionsWorksheet.set_row(0, None, header_fmt)

    # # Add border formatting to the entire data frame
    # border_fmt = workbook.add_format({'border': 1})
    # allEnforcementActionsWorksheet.conditional_format('A1:P1000',
    #                              {'type': 'cell', 'criteria': 'not equal to', 'value': '"null"', 'format': border_fmt})
    # unlitigatedEnforcementActionsWorksheet.conditional_format('A1:P1000',
    #                                 {'type': 'cell', 'criteria': 'not equal to', 'value': '"null"', 'format': border_fmt})

    # save the excel file
    writer.save()

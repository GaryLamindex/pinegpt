import {
  ActionIcon,
  Box,
  Button,
  Flex,
  Group,
  Modal,
  Stack,
  Text,
  Textarea,
  TextInput,
  Tooltip,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { IconPlaylistAdd, IconPlus } from "@tabler/icons-react";
import { useNavigate } from "@tanstack/react-location";
import { nanoid } from "nanoid";
import { useState, useEffect, useMemo } from "react";
import { db } from "../db";
import { DeletePromptModal } from "./DeletePromptModal";
import { EditPromptModal } from "./EditPromptModal";
import { Table } from "@mantine/core";
import { Line } from 'react-chartjs-2';
import { Chart } from 'react-chartjs-2';
import 'chart.js/auto';
import 'chartjs-adapter-date-fns';
import { registerables } from 'chart.js';
import dateAdapter from 'chartjs-adapter-date-fns';
import { format } from "date-fns";
import { useRef } from 'react';
import { CreatePromptModal } from './CreatePromptModal';
import { LightTheme } from '@mantine/core';




export function Prompts({ onPlay, search }: { onPlay: () => void; search: string }) {
  const navigate = useNavigate();
  const [folderPrompts, setFolderPrompts] = useState([]);
  const [csvData, setCsvData] = useState([]);
  const [drawdownData, setDrawdownData] = useState([]);
  const [infoData, setInfoData] = useState([]);
  const chartRef = useRef(null);
  const [isExpanded, setIsExpanded] = useState<string | null>(null);
  const [displayNames, setDisplayNames] = useState([]);
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: 'Example dataset',
        data: [],
        fill: false,
        backgroundColor: 'rgba(75,192,192,0.4)',
        borderColor: 'rgba(75,192,192,1)',
      },
    ],
  });
  const theme = LightTheme;

  useEffect(() => {
    const fetchTableData = async () => {
      const response = await fetch("http://localhost:5000/api/tables");
      const data = await response.json();
      const formattedData = data.map((item) => ({
        table_id: item.table_id,
        title: item.display_name, // using display_name as title here
        content: item.info_data,  // assuming the entire item is needed for content
        table_name: item.table_name,
        strategy_name: item.strategy_name

      }));
      setFolderPrompts(formattedData);
      console.log(formattedData); // <--- Add this line to verify the data
    };
    fetchTableData();
  }, []);
  
  
  useEffect(() => {
    console.log("chartData:", chartData);
  }, [chartData]);


  const fetchCsvData = async (table_id) => {
    const abortController = new AbortController();
    try {
      // Pass the signal from the abortController to the fetch API
      const response = await fetch(`http://localhost:5000/api/${table_id}/data`, { signal: abortController.signal });
      const data = await response.json();

      const { stats_data, run_data, info_data, drawdown_data} = data;

      // update chart data with run_data
      updateLineChartData(run_data);

      // update table data with stats_data
      setCsvData(stats_data);

      // update the info text area with info_data
      setInfoData(info_data);
      
      setDrawdownData(drawdown_data);
      
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Fetch aborted');
      } else {
        console.error("Error fetching CSV data:", error);
      }
    }

    return () => {
      // Abort fetch when the component is unmounted
      abortController.abort();
    };
  };

  
  
  const fetchDisplayNames = async () => {
    const response = await fetch("http://localhost:5000/api/tables");
    const data = await response.json();
    setDisplayNames(data);
  };
  
  fetchDisplayNames();
  
  
  const updateLineChartData = (runData) => {
    // Assuming the runData has columns 'date' and 'NetLiquidation'
    console.log("runData:", runData);
    const dates = runData
      .map((row) => {
        try {
          const date = new Date(row['date']);
          if (isNaN(date)) throw new Error('Invalid Date');
          const formattedDate = format(date, 'MMM d, yyyy');
          return formattedDate;
        } catch (error) {
          console.error('Error formatting date:', error.message);
          return null; // Return null for invalid dates, which will be filtered out later
        }
      })
      .filter((date) => date !== null); // Filter out invalid dates
   
    const netLiquidations = runData
      .filter((row, index) => dates[index] !== null)
      .map((row) => row['NetLiquidation']);


    console.log('Extracted Dates:', dates); // Log the dates  
    console.log('Extracted netLiquidations:', netLiquidations);

    const updatedChartData = {
      labels: dates,
      datasets: [
        {
          label: 'Net Liquidation',
          data: netLiquidations,
          fill: false,
          backgroundColor: 'rgba(75,192,192,0.4)',
          borderColor: 'rgba(75,192,192,1)',
        },
      ],
    };
  
    console.log('Updated chart data:', updatedChartData); // Log the updated chart data
    setChartData(updatedChartData);

  };
  
   

  const tableHeaders = useMemo(() => {
    if (csvData.length > 0) {
      return Object.keys(csvData[0]);
    }
    return [];
  }, [csvData]);

  const parseCsv = (csvText) => {
    const rows = csvText.split("\n");
    const header = rows[0].split(",");
    const data = rows.slice(1).map((row) => {
      const rowData = row.split(",");
      return header.reduce((acc, columnName, index) => {
        acc[columnName] = rowData[index];
        return acc;
      }, {});
    });
    return data;
  };

  
  const filteredPrompts = useMemo(
    () =>
      (folderPrompts ?? []).filter((prompt) => {
        if (!search) return true;
        return (
          prompt.title.toLowerCase().includes(search) ||
          prompt.content.toLowerCase().includes(search)
        );
      }),
    [folderPrompts, search]
  );

  const [opened, { open, close }] = useDisclosure(false);
  const [submitting, setSubmitting] = useState(false);
  const [value, setValue] = useState("");
  const [promptTitle, setPromptTitle] = useState(""); // Add state for prompt title

  const data = {
    labels: ['2018', '2019', '2020', '2021', '2022', '2023'],
    datasets: [
      {
        label: 'Example dataset',
        data: [12, 19, 3, 5, 2, 3],
        fill: false,
        backgroundColor: 'rgba(75,192,192,0.4)',
        borderColor: 'rgba(75,192,192,1)',
      },
    ],
  };
  
  const options = {
    scales: {
      x: {
        type: 'time',
        adapters: {
          date: dateAdapter,
        },
        time: {
          parser: 'MMM d, yyyy',
          unit: 'day',
          displayFormats: {
            day: 'MMM d, yyyy',
          },
          tooltipFormat: 'll',
        },
        title: {
          display: true,
          text: 'Date',
        },
      },
      y: {
        type: 'linear',
        title: {
          display: true,
          text: 'Net Liquidation',
        },
      },
    },
  };
  
  
  const tableData = [
    { id: 1, col1: 'Data 1', col2: 'Data 2', col3: 'Data 3', col4: 'Data 4' },
    { id: 2, col1: 'Data 1', col2: 'Data 2', col3: 'Data 3', col4: 'Data 4' },
    { id: 3, col1: 'Data 1', col2: 'Data 2', col3: 'Data 3', col4: 'Data 4' },
  ];

  // const handleBoxClick = async (prompt) => {
  //   setValue(prompt.content);
  //   setPromptTitle(prompt.title);
  //   await fetchCsvData(prompt.title); // Make sure prompt object has the folderName property
  //   open();
  // };
  
  const handleBoxClick = async (prompt) => {
    setValue(prompt.content);
    setPromptTitle(prompt.display_name); //use display_name instead of title
    console.log('prompt.table_id:', prompt.table_id);
    await fetchCsvData(prompt.table_id); // Pass the table_id as parameter
    open();
  };
  
  
  // // Update the handleValueClick function to pass item.id as the item_id parameter
  // const handleValueClick = async (event, prompt, item) => {
  //   event.stopPropagation();
  //   setValue(item.value);
  //   setPromptTitle(prompt.title);
  //   console.log('prompt.title:', prompt.title);
  //   console.log('item.Value:', item.value);
  //   console.log('item.id:', item.id);
  //   await fetchCsvData(`${prompt.title}`, item.id); // Pass the item_id parameter
  //   open();
  // };

  const handleSubmit = async (event) => {
    try {
      setSubmitting(true);
      event.preventDefault();
      const id = nanoid();
      await db.chats.add({
        id,
        description: "New Chat",
        totalTokens: 0,
        createdAt: new Date(),
      });


      // convert JSON objects to string
      let csvDataString = JSON.stringify(csvData, null, 2);
      let drawdownDataString = JSON.stringify(drawdownData, null, 2);
      let parsedInfoDataString = JSON.stringify(infoData, null, 2);

      let strategyDescriptionString = csvDataString + "\n" + drawdownDataString + "\n" + parsedInfoDataString;

      console.log('strategyDescriptionString:', strategyDescriptionString); 
      
      await db.messages.add({
        id: nanoid(),
        chatId: id,
        content: strategyDescriptionString,
        role: "assistant",
        createdAt: new Date(),
      });
            

      notifications.show({
        title: "Saved",
        message: "Chat created",
      });
      close();
      navigate({ to: `/chats/${id}` });
    } catch (error: any) {
      notifications.show({
        title: "Error",
        message: error.message || "An error occurred while creating the chat.",
        color: "red",
      });
    } finally {
      setSubmitting(false);
    }
  };
  
  let parsedInfoData = typeof infoData === 'string' ? JSON.parse(infoData) : infoData;
  return (
    <>
      
      {filteredPrompts.map((prompt) => (
        <Box key={prompt.id}>
          <Flex
            key={prompt.id}
            sx={(theme) => ({
              marginTop: 1,
              padding: theme.spacing.xs,
              "&:hover": {
                backgroundColor:
                  theme.colorScheme === "dark"
                    ? theme.colors.dark[6]
                    : theme.colors.gray[1],
              },
            })}
          >
            <Box
              onClick={() => handleBoxClick(prompt)}
              sx={(theme) => ({
                flexGrow: 1,
                width: 0,
                fontSize: theme.fontSizes.sm,
                cursor: "pointer",
              })}
            >
              <Text
                weight={500}
                sx={{
                  textOverflow: "ellipsis",
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                }}
              >
                {prompt.title}
              </Text>
            </Box>
            <Group spacing="none">
            <EditPromptModal prompt={prompt} />
              <DeletePromptModal prompt={prompt} />
            </Group>
          </Flex>
          {isExpanded === prompt.id && (
            <Box>
              {JSON.parse(prompt.content).map((item) => (
                <Text key={item.id} onClick={(event) => handleValueClick(event, prompt, item)}>
                  {item.value}
                </Text>
              ))}
            </Box>
          )}

        </Box>
      ))}
      

      <Modal key={value} opened={opened} onClose={close} title={promptTitle} size="70%">
        <pre style={{ whiteSpace: "pre-wrap", wordWrap: "break-word" }}>{value}</pre>
        <form onSubmit={handleSubmit}>
          <Stack>
      {/* Information Table */}
          <div style={{ marginBottom: "16px" }}>
            <strong>Strategy Information:</strong>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '16px' }}>

              {Object.entries(parsedInfoData).map(([key, value], index) => {
                  console.log(`${key}: ${String(value)}`);
                  return (
                      <div key={index}>
                          <strong>{key}:</strong> {String(value)}
                      </div>
                  );
              })}

            </div>
          </div>
          
          <div style={{ marginBottom: "16px" }}>
            <strong>Strategy Statistic:</strong>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '16px' }}>

              {csvData.map((row, index) => (
                <>
                  {tableHeaders.map((header, colIndex) => (
                    <div key={`${index}-${colIndex}`}>
                      <strong>{header}:</strong> {typeof row[header] === 'string' ? row[header] : JSON.stringify(row[header])}
                    </div>
                  ))}
                </>
              ))}
            </div>
          </div>

          {/* New Strategy Drawdown Section */}
          <div style={{ marginBottom: "16px" }}>
            <strong>Strategy Drawdown:</strong>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '16px' }}>

              {drawdownData.map((row, index) => (
                <>
                  {Object.keys(row).map((key, innerIndex) => (
                    <div key={`${index}-${innerIndex}`}>
                      <strong>{key}:</strong> {typeof row[key] === 'string' ? row[key] : JSON.stringify(row[key])}
                    </div>
                  ))}
                </>
              ))}

            </div>
          </div>


          {/* Chart component */}
          <div style={{ flex: '1 0 auto', width: '100%', marginTop: '16px' }}>
            <Line data={chartData} options={options} />
          </div>
            <Button type="submit" loading={submitting}>
              Create Chat
            </Button>
          </Stack>
        </form>

        


      </Modal>
    </>
  );
}

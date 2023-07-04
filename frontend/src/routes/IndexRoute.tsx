import {
  Badge,
  Button,
  Center,
  Container,
  Group,
  SimpleGrid,
  Text,
  ThemeIcon,
} from "@mantine/core";
import {
  IconCloudDownload,
  IconCurrencyDollar,
  IconKey,
  IconLock,
  IconNorthStar,
} from "@tabler/icons-react";
import { useLiveQuery } from "dexie-react-hooks";
import { Logo } from "../components/Logo";
import { SettingsModal } from "../components/SettingsModal";
import { db } from "../db";
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
import { DateTime } from 'luxon';

export function IndexRoute() {
  const id = 0;
  const [csvData, setCsvData] = useState([]);
  const [infoData, setInfoData] = useState([]);
  const [drawdownData, setDrawdownData] = useState([]);
  const [chartData, setChartData] = useState({});
  const [runData, setRunData] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const [currentTime, setCurrentTime] = useState(DateTime.now().setZone('America/New_York'));

  const toggleExpand = () => {
    event.preventDefault();
    setIsExpanded(!isExpanded);
  };

  const dataToRender = isExpanded ? [...runData].reverse() : [...runData].slice(-20).reverse();
  const drawdownDataToRender = isExpanded ? [...drawdownData].reverse() : [...drawdownData].slice(0, 5).reverse();
  
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(DateTime.now().setZone('America/New_York'));
    }, 1000);
    
    return () => {
      clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    fetchCsvData(id);  // replace "your_table_id" with your actual table ID
  }, []);
  
  useEffect(() => {
    console.log("chartData:", chartData);
  }, [chartData]);
  

  const fetchCsvData = async () => {
    const abortController = new AbortController();
    try {
      const response = await fetch(`http://localhost:5000/api/${id}/data`, { signal: abortController.signal });
      const data = await response.json();
      console.log('Fetched data:', data);

      const { stats_data, run_data, info_data, drawdown_data, transaction_data} = data;
      if (run_data != null) {
        console.log('run_data is available:', run_data);
        updateLineChartData(run_data);
        setRunData(run_data)
      } else {
        console.error('run_data is undefined');
      }
      if (stats_data!= null) {
        console.log('stats_data is available:', stats_data);
        setCsvData(stats_data);
      } else {
        console.error('stats_data is undefined');
      }
      if (info_data != null) {
        console.log('info_data is available:', info_data);
        let parsedInfoData;
        try {
          parsedInfoData = JSON.parse(info_data);
        } catch (error) {
          console.error('Failed to parse info_data:', error);
        }
        setInfoData(parsedInfoData);
      } else {
        console.error('info_data is undefined');
      }
      
      if (drawdown_data!= null) {
        console.log('drawdown_data is available:', drawdown_data);
        setDrawdownData(drawdown_data);
      } else {
        console.error('drawdown_data is undefined');
      }

      if (transaction_data!= null) {
        console.log('transaction_data is available:', transaction_data);
        setTransactionData(transaction_data);
      }
      
    } catch (error) {
      if (error.name === 'AbortError') {
        console.log('Fetch aborted');
      } else {
        console.error("Error fetching CSV data:", error);
      }
    }

    return () => {
      abortController.abort();
    };
  };
  
  const updateLineChartData = (run_data) => {
    if (!run_data) {
      console.error('run_data is undefined');
      return;
    }
  
    console.log('run_data:', run_data); // <---- add this log
  
    const dates = run_data.map(row => row.date);
    const netLiquidations = run_data.map(row => row.NetLiquidation);
  
    console.log('dates:', dates); // <---- add this log
    console.log('netLiquidations:', netLiquidations); // <---- add this log
  
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
  
    console.log('updatedChartData:', updatedChartData);
    
    setChartData(updatedChartData);

  };
  



  return (
    <div style={{width: '95%', height: '100vh', margin: '0 16px 16px 16px'}}>
      <form>
        <Stack>

          <div style={{ flex: '1 0 auto', width: '100%', height: '50vh', marginTop: '16px' }}>
            {chartData && Object.keys(chartData).length > 0 && <Line data={chartData} options={{ responsive: true, maintainAspectRatio: false  }} />}
          </div>


          <div style={{ flex: '1 0 auto', width: '100%', marginTop: '16px' }}>
            <button type="button" onClick={toggleExpand}>{isExpanded ? 'Collapse' : 'Expand'}</button>
            <span style={{ float: 'right', marginRight: '10px' }}>{currentTime.toLocaleString(DateTime.TIME_WITH_SECONDS)}</span>
            <table style={{ width: '100%', borderCollapse: 'collapse', borderRadius: '10px', overflow: 'hidden' }}>
              <thead>
                <tr>
                  <th style={{ width: '1fr', padding: '10px', backgroundColor: '#f8f8f8' }}>Date</th>
                  <th style={{ width: '1fr', padding: '10px', backgroundColor: '#f8f8f8' }}>Action</th>
                  <th style={{ width: '1fr', padding: '10px', backgroundColor: '#f8f8f8' }}>Quantity</th>
                  <th style={{ width: '1fr', padding: '10px', backgroundColor: '#f8f8f8' }}>Price</th>
                  <th style={{ width: '1fr', padding: '10px', backgroundColor: '#f8f8f8' }}>TQQQ Price</th>
                  <th style={{ width: '1fr', padding: '10px', backgroundColor: '#f8f8f8' }}>Net Liquidation</th>
                </tr>
              </thead>
              <tbody>
                {dataToRender.map((row, index) => (
                  <tr key={index}>
                    <td style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>{row.date}</td>
                    <td style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>
                      {row.action_TQQQ && (row.action_TQQQ.includes("BUY") ? "BUY" :
                        row.action_TQQQ.includes("SELL") ? "SELL" : row.action_TQQQ)}
                    </td>
                    <td style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>{row.totalQuantity_TQQQ}</td>
                    <td style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>
                      {row.avgPrice_TQQQ ? Math.floor(row.avgPrice_TQQQ * 10) / 10 : ''}
                    </td>
                    <td style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>
                      {Math.floor(row['mktPrice_TQQQ '] * 10) / 10}
                    </td>
                    <th style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>
                      {Math.floor(row.NetLiquidation * 10) / 10}
                    </th>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>


          <div style={{ marginBottom: "16px", backgroundColor: '#f8f8f8', borderRadius: '10px', padding: '16px' }}>
            <strong>Strategy Information:</strong>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '16px' }}>
              {Object.entries(infoData).map(([key, value], index) => (
                <div key={index} style={{ padding: '10px', borderBottom: index < Object.entries(infoData).length - 1 ? '1px solid #ddd' : 'none' }}>
                    <strong>{key}:</strong> {String(value)}
                </div>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: "16px", backgroundColor: '#f8f8f8', borderRadius: '10px', padding: '16px' }}>
            <strong>Strategy Statistic:</strong>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '16px' }}>
              {csvData.map((row, index) => (
                <>
                  {Object.keys(row).map((key, colIndex) => (
                    <div key={`${index}-${colIndex}`} style={{ padding: '10px', borderBottom: colIndex < Object.keys(row).length - 1 ? '1px solid #ddd' : 'none' }}>
                      <strong>{key}:</strong> 
                      {typeof row[key] === 'number' ? parseFloat(row[key].toFixed(2)) : ''}
                    </div>
                  ))}
                </>
              ))}
            </div>
          </div>


          <div style={{ flex: '1 0 auto', width: '100%', marginTop: '16px', backgroundColor: '#f8f8f8', borderRadius: '10px', padding: '16px' }}>
            <strong>Strategy Drawdown:</strong>
            <button type="button" onClick={toggleExpand} style={{ float: 'right', marginBottom: '10px' }}>{isExpanded ? 'Collapse' : 'Expand'}</button>

            <table style={{ width: '100%', tableLayout: 'fixed', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ borderBottom: '1px solid #ddd', textAlign: 'left', padding: '10px' }}>Drawdown</th>
                  <th style={{ borderBottom: '1px solid #ddd', textAlign: 'left', padding: '10px' }}>Drawdown period</th>
                  <th style={{ borderBottom: '1px solid #ddd', textAlign: 'left', padding: '10px' }}>Drawdown days</th>
                  <th style={{ borderBottom: '1px solid #ddd', textAlign: 'left', padding: '10px' }}>Recovery date</th>
                  <th style={{ borderBottom: '1px solid #ddd', textAlign: 'left', padding: '10px' }}>Recovery days</th>
                </tr>
              </thead>
              <tbody>
                {drawdownDataToRender.map((row, index) => (
                  <tr key={index}>
                    <td style={{ borderBottom: index < drawdownDataToRender.length - 1 ? '1px solid #ddd' : 'none', padding: '10px' }}>{Math.floor(row['Drawdown'] * 1000) / 10}%</td>
                    <td style={{ borderBottom: index < drawdownDataToRender.length - 1 ? '1px solid #ddd' : 'none', padding: '10px' }}>{row['Drawdown period']}</td>
                    <td style={{ borderBottom: index < drawdownDataToRender.length - 1 ? '1px solid #ddd' : 'none', padding: '10px' }}>{row['Drawdown days']}</td>
                    <td style={{ borderBottom: index < drawdownDataToRender.length - 1 ? '1px solid #ddd' : 'none', padding: '10px' }}>{row['Recovery date']}</td>
                    <td style={{ borderBottom: index < drawdownDataToRender.length - 1 ? '1px solid #ddd' : 'none', padding: '10px' }}>{row['Recovery days']}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

        </Stack>
      </form>
    </div>
  );
};


// export function IndexRoute() {
//   const settings = useLiveQuery(() => db.settings.get("general"));
//   const { openAiApiKey } = settings ?? {};
//   console.log("IndexRoute is rendered");
//   return (
//     <>
//       <Center py="xl" sx={{ height: "100%" }}>
//         <Container size="sm">
//           <Badge mb="lg">GPT-4 Ready</Badge>
//           <Text>
//             <Logo style={{ maxWidth: 240 }} />
//           </Text>
//           <Text mt={4} size="xl">
//             Not just another ChatGPT user-interface!
//           </Text>
//           <SimpleGrid
//             mt={50}
//             cols={3}
//             spacing={30}
//             breakpoints={[{ maxWidth: "md", cols: 1 }]}
//           >
//             {features.map((feature) => (
//               <div key={feature.title}>
//                 <ThemeIcon variant="outline" size={50} radius={50}>
//                   <feature.icon size={26} stroke={1.5} />
//                 </ThemeIcon>
//                 <Text mt="sm" mb={7}>
//                   {feature.title}
//                 </Text>
//                 <Text size="sm" color="dimmed" sx={{ lineHeight: 1.6 }}>
//                   {feature.description}
//                 </Text>
//               </div>
//             ))}
//           </SimpleGrid>
//           <Group mt={50}>
//             <SettingsModal>
//               <Button
//                 size="md"
//                 variant={openAiApiKey ? "light" : "filled"}
//                 leftIcon={<IconKey size={20} />}
//               >
//                 {openAiApiKey ? "Change OpenAI Key" : "Enter OpenAI Key"}
//               </Button>
//             </SettingsModal>
//             {!window.todesktop && (
//               <Button
//                 component="a"
//                 href="https://dl.todesktop.com/230313oyppkw40a"
//                 // href="https://download.chatpad.ai/"
//                 size="md"
//                 variant="outline"
//                 leftIcon={<IconCloudDownload size={20} />}
//               >
//                 Download Desktop App
//               </Button>
//             )}
//           </Group>
//         </Container>
//       </Center>
//     </>
//   );
// }

const features = [
  {
    icon: IconCurrencyDollar,
    title: "Free and open source",
    description:
      "This app is provided for free and the source code is available on GitHub.",
  },
  {
    icon: IconLock,
    title: "Privacy focused",
    description:
      "No tracking, no cookies, no bullshit. All your data is stored locally.",
  },
  {
    icon: IconNorthStar,
    title: "Best experience",
    description:
      "Crafted with love and care to provide the best experience possible.",
  },
];

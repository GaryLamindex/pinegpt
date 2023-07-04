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

const OnePager = (props) => {
  const { id } = props;
  const [csvData, setCsvData] = useState([]);
  const [infoData, setInfoData] = useState([]);
  const [drawdownData, setDrawdownData] = useState([]);
  const [chartData, setChartData] = useState({});
  const [submitting, setSubmitting] = useState(false);
  
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

      const { stats_data, run_data, info_data, drawdown_data} = data;
      if (run_data != null) {
        console.log('run_data is available:', run_data);
        updateLineChartData(run_data);

      } else {
        console.error('run_data is undefined');
      }
      if (stats_data!= null) {
        console.log('stats_data is available:', stats_data);
        setCsvData(stats_data);
      } else {
        console.error('stats_data is undefined');
      }
      if (info_data!= null) {
        console.log('info_data is available:', info_data);
        setInfoData(JSON.parse(info_data));
      } else {
        console.error('info_data is undefined');
      }
      if (drawdown_data!= null) {
        console.log('drawdown_data is available:', drawdown_data);
        setDrawdownData(drawdown_data);
      } else {
        console.error('drawdown_data is undefined');
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
    const dates = run_data.map(row => row.date);
    const netLiquidations = run_data.map(row => row.NetLiquidation);

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
    <Modal opened={true} onClose={() => {}} title="My Title" size="70%">
      <pre style={{ whiteSpace: "pre-wrap", wordWrap: "break-word" }}>{infoData}</pre>
      <form>
        <Stack>
          <div style={{ marginBottom: "16px" }}>
            <strong>Strategy Information:</strong>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '16px' }}>
              {Object.entries(infoData).map(([key, value], index) => (
                <div key={index}>
                    <strong>{key}:</strong> {String(value)}
                </div>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: "16px" }}>
            <strong>Strategy Statistic:</strong>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '16px' }}>
              {csvData.map((row, index) => (
                <>
                  {Object.keys(row).map((key, colIndex) => (
                    <div key={`${index}-${colIndex}`}>
                      <strong>{key}:</strong> {String(row[key])}
                    </div>
                  ))}
                </>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: "16px" }}>
            <strong>Strategy Drawdown:</strong>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', marginTop: '16px' }}>
              {drawdownData.map((row, index) => (
                <>
                  {Object.keys(row).map((key, innerIndex) => (
                    <div key={`${index}-${innerIndex}`}>
                      <strong>{key}:</strong> {String(row[key])}
                    </div>
                  ))}
                </>
              ))}
            </div>
          </div>

          <div style={{ flex: '1 0 auto', width: '100%', marginTop: '16px' }}>
            <Line data={chartData} options={{ responsive: true }} />
          </div>

          <Button type="submit" loading={submitting}>
            Create Chat
          </Button>
        </Stack>
      </form>
    </Modal>
  );
};

export default OnePager;


import {
  ActionIcon,
  Button,
  Modal,
  Stack,
  Textarea,
  TextInput,
  Tooltip,
} from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { IconPlaylistAdd, IconPlus } from "@tabler/icons-react";
import { nanoid } from "nanoid";
import { useEffect, useState } from "react";
import { db } from "../db";
import { useNavigate } from "@tanstack/react-location";
import axios from "axios"; // Don't forget to install axios: npm install axios


export function CreatePromptModal({ content, openModal }: { content?: string; openModal: () => void }) {
  const [opened, { open, close }] = useDisclosure(false);
  const [submitting, setSubmitting] = useState(false);

  const navigate = useNavigate();

  const [value, setValue] = useState("");
  useEffect(() => {
    setValue(content ?? "");
  }, [content]);

  return (
    <>
      {content ? (
        <Tooltip label="Save Pinescript" position="left">
          <ActionIcon onClick={openModal}>
            <IconPlaylistAdd opacity={0.5} size={20} />
          </ActionIcon>
        </Tooltip>
      ) : (
        <Button fullWidth onClick={open} leftIcon={<IconPlus size={20} />}>
          Restart Backtest
        </Button>
      )}
        <Modal opened={opened} onClose={close} title="Restart Backtest" size="lg">
          <form
            onSubmit={async (event) => {
              try {
                setSubmitting(true);
                event.preventDefault();
                        
                const marginRatio = 3.24; // Replace this with the desired margin ratio value
                const response = await axios.post("http://localhost:5000/restart", {
                  margin_ratio: marginRatio,
                });
            
                if (response.status === 200) {
                  console.log("Response:", response.data);
                } else {
                  console.error("Error:", response.status, response.statusText);
                }
            
                notifications.show({
                  title: "Saved",
                  message: "New signal created",
                });
                close();
              } catch (error: any) {
                // Add the modified error handling block here
              } finally {
                setSubmitting(false);
              }
            }}
            
          >
            <Stack>

              <div style={{ marginBottom: '16px' }}>
                <strong>Strategy That Will be Generated:</strong>
                <pre style={{ whiteSpace: 'pre-wrap', wordWrap: 'break-word' }}>{value}</pre>

                <table style={{ width: '100%', marginTop: '16px' }}>
                  <thead>
                    <tr>
                      <th style={{textAlign: "left", border: '1px solid grey'}}>Strategy Name</th>
                      <th style={{textAlign: "left", border: '1px solid grey'}}>Variable Parameters</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr>
                      <td style={{border: '1px solid grey'}}>Accelerating Dual Momentum</td>
                      <td style={{border: '1px solid grey'}}>
                        Backtest Period: 2015-01-01 - 2020-01-01<br />
                        Rebalance Frequency: Monthly<br />
                        Asset 1: SPY<br />
                        Asset 2: QQQ<br />
                        Bond: TIP<br />
                      </td>
                    </tr>
                    <tr>
                      <td style={{border: '1px solid grey'}}>Accelerating Dual Momentum</td>
                      <td style={{border: '1px solid grey'}}>
                        Backtest Period: 2015-01-01 - 2020-01-01<br />
                        Rebalance Frequency: Monthly<br />
                        Asset 1: ARKK<br />
                        Asset 2: QQQ<br />
                        Bond: TIP<br />
                      </td>
                    </tr>
                    <tr>
                      <td style={{border: '1px solid grey'}}>Rebalance Margin With Max Drawdown Control</td>
                      <td style={{border: '1px solid grey'}}>
                        Backtest Period: 2015-01-01 - 2020-01-01<br />
                        Rebalance Frequency: Monthly<br />
                        Asset 1: QQQ<br />
                        Excess Liquidity Ratio: 8%<br />
                      </td>
                    </tr>
                    <tr>
                      <td style={{border: '1px solid grey'}}>Rebalance Margin With Max Drawdown Control</td>
                      <td style={{border: '1px solid grey'}}>
                        Backtest Period: 2015-01-01 - 2020-01-01<br />
                        Rebalance Frequency: Monthly<br />
                        Asset 1: QQQ<br />
                        Excess Liquidity Ratio: 9%<br />
                      </td>
                    </tr>
                    <tr>
                      <td style={{border: '1px solid grey'}}>Rebalance Margin With Max Drawdown Control</td>
                      <td style={{border: '1px solid grey'}}>
                        Backtest Period: 2015-01-01 - 2020-01-01<br />
                        Rebalance Frequency: Monthly<br />
                        Asset 1: SPY<br />
                        Excess Liquidity Ratio: 8%<br />
                      </td>
                    </tr>
                    <tr>
                      <td style={{border: '1px solid grey'}}>Rebalance Margin With Max Drawdown Control</td>
                      <td style={{border: '1px solid grey'}}>
                        Backtest Period: 2015-01-01 - 2020-01-01<br />
                        Rebalance Frequency: Monthly<br />
                        Asset 1: SPY<br />
                        Excess Liquidity Ratio: 9%<br />
                      </td>
                    </tr>
                    <tr>
                      <td style={{border: '1px solid grey'}}>...</td>
                      <td style={{border: '1px solid grey'}}>...</td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <Button type="submit" loading={submitting}>
                Restart Backtest
              </Button>
            </Stack>
          </form>
        </Modal>

    </>
  );
}
